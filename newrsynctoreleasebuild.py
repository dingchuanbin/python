#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:ding

import os
import subprocess
import sys
import xlrd
import re

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
    for i in prorownumindex:
        appstartnum = prorownum[i]
        appinfodict = {}
        if prorownumindex.index(i)+1 > len(prorownumindex) - 1:
            appendnum = ws.nrows
        else:
            appendnum = prorownum[prorownumindex[prorownumindex.index(i) + 1]]
        for n in range(appstartnum,appendnum):
            appinfodict[ws.cell_value(n, colnum_hash[appindex])]=ws.cell_value(n,colnum_hash['appversion'])
            proinfodict = {'version':'','apps':[]}
            proinfodict['apps'] = appinfodict
            proinfodict['version'] = ws.cell_value(appstartnum,colnum_hash['version'])
            proapps[prorownumindex[prorownumindex.index(i)]] = proinfodict
    return proapps
def rsyncapp(rsyncsrcdir,app,rsynctargetdir,configid=''):
    rsyncsrcconfigdir = rsyncsrcdir + '_config'
    rsynctargetconfigdir = rsynctargetdir + '_config'
    cmd = "rsync -avrz --delete %s/%s %s/" % (rsyncsrcdir, app, rsynctargetdir)
    subprocess.check_call(cmd, shell=True)
    if os.path.exists(rsyncsrcconfigdir + '/' + app):
        if not os.path.exists(rsynctargetconfigdir + '/' + app):
            os.makedirs(rsynctargetconfigdir + '/' + app)
        configfiles = os.listdir(rsyncsrcconfigdir + '/' + app)
        for configfile in configfiles:
            if configfile.startswith('.'):
                pass
            elif configfile.endswith(('.properties','.xml','.js','.yml')):
                cmd = "rsync -avrz --delete %s/%s/%s %s/%s/%s" % (\
                    rsyncsrcconfigdir,\
                    app,\
                    configfile,\
                    rsynctargetconfigdir,\
                    app,\
                    configfile\
                    )
                subprocess.check_call(cmd, shell=True)
            elif configid == '' and len(configfile.split('_')) > 1 :
                pass
            else:
                dstconfigname = configfile
                print(dstconfigname)
                if configfile.endswith(configid):
                    dstconfigname = configfile.split('_')[0]
                cmd = "rsync -avrz --delete %s/%s/%s %s/%s/%s" % (\
                    rsyncsrcconfigdir,\
                    app,\
                    configfile,\
                    rsynctargetconfigdir,\
                    app,\
                    dstconfigname)
                subprocess.check_call(cmd, shell=True)
#写入版本号
def writeversion(key,vsrcfile,appversionf):
    uvinfo = ''
    with open(vsrcfile,'r') as f:
        for line in f.readlines():
            if line.startswith(key + "="):
                uvinfo = (line.strip().split(key + "=")[1])
            else:
                print("未找到" + key + "的版本")
    with open(appversionf,'w') as v:
        v.write(uvinfo)
def allsync(filename,sheetindex='',buildsdir='',releasebuildsdir=''):
    syncapplist = sys.argv[2]
    syncapplist = syncapplist.split(',')
    proinfodict = project_apps(filename, sheetindex, 'project', 'appname')
    #多项目配置拷贝
    configidlist=['good','bitbullex']
    for configid in configidlist:
        if re.match(configid,sheetindex):
            configid=configid
        else:
            configid=''
    rsynctargetdir = releasebuildsdir + '/' + sheetindex
    if (syncapplist[0] == 'all') and (len(syncapplist) == 1):
        for pro in proinfodict.keys():
            appslist = proinfodict[pro]['apps'].keys()
            for app in appslist:
                appversion = proinfodict[pro]['apps'][app]
                rsyncsrcdir = buildsdir + '/' + pro.lower() + '_' + appversion
                rsyncapp(rsyncsrcdir,app,rsynctargetdir,configid)
                writeversion(app,\
                             rsyncsrcdir + '/' + appversion + '_version.properties',\
                             rsynctargetdir + '/' + app + '/version'\
                             )
    elif (syncapplist[0] in proinfodict.keys()) and (len(syncapplist) == 1):
        pro = syncapplist[0]
        appslist = proinfodict[pro]['apps'].keys()
        for app in appslist:
            appversion = proinfodict[pro]['apps'][app]
            rsyncsrcdir = buildsdir + '/' + pro.lower() + '_' + appversion
            rsyncapp(rsyncsrcdir, app, rsynctargetdir, configid)
            writeversion(app, \
                         rsyncsrcdir + '/' + appversion + '_version.properties',\
                         rsynctargetdir + '/' + app + '/version'\
                         )
    elif len(syncapplist) >= 1:
        for pro in proinfodict.keys():
            appslist = proinfodict[pro]['apps'].keys()
            for app in  syncapplist:
                if app in appslist:
                    appversion = proinfodict[pro]['apps'][app]
                    rsyncsrcdir = buildsdir + '/' + pro.lower() + '_' + appversion
                    rsyncapp(rsyncsrcdir, app, rsynctargetdir, configid)
                    writeversion(app,\
                                 rsyncsrcdir + '/' + appversion + '_version.properties', \
                                 rsynctargetdir + '/' + app + '/version' \
                                 )
                else:
                    print("未找到" + app)
if __name__ == '__main__':
    sheetname = sys.argv[1]
    allsync('/home/dami/JenkinsHome/workspace/builds/releaseconfig/BBST.xlsx',
            sheetname,'/home/dami/JenkinsHome/workspace/builds/releasebuilds',
            '/home/dami/JenkinsHome/workspace/builds/releasebuilds')
