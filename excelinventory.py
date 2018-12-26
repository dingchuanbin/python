#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:ding
import argparse
import xlrd
import json
import sys
import subprocess

def open_file(filename):
    try:
        data = xlrd.open_workbook(filename)
        return data
    except Exception as e:
        print(str(e))
hostinfolist = []
def inventory(filename,sheetbyname='',group_index='',host_index=''):
    wb = open_file(filename)
    ws = wb.sheet_by_name(sheetbyname)
    column_hash = {}
    for i in range(ws.ncols):
        column_hash[ws.cell_value(0, i)] = i
    group_column_name = column_hash[group_index]
    host_column_name = column_hash[host_index]
    pass_column_name = column_hash['ansible_ssh_pass']
    user_column_name = column_hash['ansible_ssh_user']
    group_hash = {}
    multiapp = None
    for i in range(1,ws.nrows):
        appname = ws.cell_value(i, group_column_name)
        if  multiapp == appname:
            hostlist = hostlist
        else:
            hostlist = []
        varsdict = {}
        if [ws.cell_value(i,host_column_name),ws.cell_value(i,user_column_name),ws.cell_value(i,pass_column_name)] not in hostinfolist:
            hostinfolist.append([ws.cell_value(i,host_column_name),ws.cell_value(i,user_column_name),ws.cell_value(i,pass_column_name)])
        group_hash[ws.cell_value(i, group_column_name)] = {'hosts':[],'vars':{}}
        hostlist.append(ws.cell_value(i,host_column_name))
        for n in  range(ws.ncols):
            if n not in [0,1,group_column_name,host_column_name]:
                varsdict[ws.cell_value(0,n)]=ws.cell_value(i,n)
        group_hash[ws.cell_value(i, group_column_name)]['hosts'] = hostlist
        group_hash[ws.cell_value(i, group_column_name)]['vars'] = varsdict
        multiapp = ws.cell_value(i, group_column_name)
    return json.dumps(group_hash,indent=4)

if __name__ == "__main__":
    hostinventory = inventory('/home/dami/JenkinsHome/workspace/builds/releaseconfig/BBST.xlsx', 'Test', 'appname', 'ip')
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--list', help='hosts list', action='store_true')
    parser.add_argument('-i', '--init', help='private rsa key', action='store_true')
    args = vars(parser.parse_args())
    # for hostinfo in hostinfolist:
    #     username = hostinfo[1]
    #     password = hostinfo[2]
    #     ip = hostinfo[0]
    #     cmd = "sshpass -p " + password + " rsync -avz /home/" + username + "/.ssh/id_rsa.pub " \
    #           + username + "@" + ip + ":/home/" + username + "/.ssh/authorized_keys"
    #     print(cmd)
    if args['list']:
        print(hostinventory)
    elif args['init']:
        cmd = "ansible -i excelinventory.py all -m ping"
        subprocess.check_call(cmd, shell=True)
        for hostinfo in hostinfolist:
            username = hostinfo[1]
            password = hostinfo[2]
            ip = hostinfo[0]
            cmd = "sshpass -p " + password + " rsync -avz /home/" + username + "/.ssh/id_rsa.pub " \
                  + username + "@" + ip + ":/home/" + username + "/.ssh/authorized_keys"
            subprocess.check_call(cmd, shell=True)
