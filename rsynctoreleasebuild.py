#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:ding

import os
import shutil
import subprocess
import sys
import xlrd


def open_excel(filename):
    try:
        data = xlrd.open_workbook(filename)
        return data
    except Exception as e:
        print(str(e))
def project_apps(filename,sheetindex='',projectindex='',appindex=''):
    wb = open_excel(filename)
    ws = wb.sheet_by_name(sheetindex)
    colnum_hash = {}
    for i in range(ws.ncols):
        colnum_hash[ws.cell_value(0,i)] = i
    procolnum = colnum_hash[projectindex]
    rownum_hash = {}
    for i in range(ws.nrows):
        rownum_hash[ws.cell_value(i,0)] = i
    pronames = []
    prorownum = {}
    for i in range(1,ws.nrows):
        if ws.cell_value(i,procolnum):
            pronames.append(ws.cell_value(i,procolnum))
            prorownum[ws.cell_value(i,procolnum)] = rownum_hash[ws.cell_value(i,procolnum)]
    proapps = {}
    prorownumindex = list(prorownum.keys())
    # print(prorownumindex)
    for i in prorownumindex:
        applist = []
        appstartnum = prorownum[i]
        if prorownumindex.index(i)+1 > len(prorownumindex) - 1:
            appendnum = ws.nrows
        else:
            appendnum = prorownum[prorownumindex[prorownumindex.index(i) + 1]]
        # print(prorownumindex[prorownumindex.index(i)],appstartnum,appendnum)
        for n in range(appstartnum,appendnum):
            # print(ws.cell_value(n,colnum_hash[appindex]))
            applist.append(ws.cell_value(n,colnum_hash[appindex]))
            proinfodict = {'version':'','apps':[]}
            # proapps[prorownumindex[prorownumindex.index(i)]['version'] = ws.cell_value(appstartnum,colnum_hash['version'])
            # proapps[prorownumindex[prorownumindex.index(i)]] = applist
            proinfodict['apps'] = applist
            proinfodict['version'] = ws.cell_value(appstartnum,colnum_hash['version'])
            proapps[prorownumindex[prorownumindex.index(i)]] = proinfodict
    return proapps
def rsync_app(filename,sheetindex='',srcdir='',targetdir=''):
    syncapplist = sys.argv[2]
    syncapplist = syncapplist.split(',')
    proinfodict = project_apps(filename, sheetindex, 'project', 'appname')
    for pro in proinfodict.keys():
        appslist = proinfodict[pro]['apps']
        proversion = proinfodict[pro]['version']
        rsyncsrcdir = srcdir + '/' + pro.lower() + '_' + proversion
        rsynctargetdir = targetdir + '/' + sheetindex
        rsyncsrcconfigdir = srcdir + '/' + pro.lower() + '_' + proversion + '_config'
        rsynctargetconfigdir = targetdir + '/' + sheetindex + '_config'
        if (syncapplist[0] == 'all') and (len(syncapplist) == 1):
            for app in appslist:
                cmd = "rsync -avrz --delete %s/%s %s/" %(rsyncsrcdir,app,rsynctargetdir)
                subprocess.check_call(cmd, shell=True)
                if os.path.exists(rsyncsrcconfigdir):
                    cmd = "rsync -avrz --delete %s/%s %s/" % (rsyncsrcconfigdir,app,rsynctargetconfigdir)
                    subprocess.check_call(cmd, shell=True)
        elif (syncapplist[0] == pro) and (len(syncapplist) == 1):
            for app in appslist:
                cmd = "rsync -avrz --delete %s/%s %s/" % (rsyncsrcdir, app, rsynctargetdir)
                subprocess.check_call(cmd, shell=True)
                if os.path.exists(rsyncsrcconfigdir):
                    cmd = "rsync -avrz --delete %s/%s %s/" % (rsyncsrcconfigdir, app, rsynctargetconfigdir)
                    subprocess.check_call(cmd, shell=True)
            break
        elif len(syncapplist) >= 1:
            for app in syncapplist:
                if app in appslist:
                    cmd = "rsync -avrz --delete %s/%s %s/" % (rsyncsrcdir, app, rsynctargetdir)
                    subprocess.check_call(cmd, shell=True)
                    if os.path.exists(rsyncsrcconfigdir):
                        cmd = "rsync -avrz --delete %s/%s %s/" % (rsyncsrcconfigdir, app, rsynctargetconfigdir)
                        subprocess.check_call(cmd, shell=True)
sheetname = sys.argv[1]
# rsync_app('BBST.xlsx','Test','/home/dami/JenkinsHome/workspace/builds/releasebuilds','/home/dami/JenkinsHome/workspace/builds/releasebuilds')
rsync_app('/home/dami/JenkinsHome/workspace/builds/releaseconfig/BBST.xlsx',sheetname,'/home/dami/JenkinsHome/workspace/builds/releasebuilds','/home/dami/JenkinsHome/workspace/builds/releasebuilds')
