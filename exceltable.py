#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:ding
import argparse
import xlrd
import json
import sys
import subprocess
import re


class Exceldb(object):
    def __init__(self,filename):
        self.filename = filename

    def book(self):
        try:
            book = xlrd.open_workbook(self.filename)
            return book
        except Exception as e:
            print(str(e))

    def t_sheets(self):
        book = self.book()
        s_names = book.sheet_names()
        ws = {}
        for i in s_names:
            ws[i] = book.sheet_by_name(i)
        return ws

class Ex_table(object):

    def __init__(self,filename,t_name):
        self.filename = filename
        self.t_name = t_name
        self.t_table = Exceldb(self.filename).t_sheets()[self.t_name]

    def col_field(self):
        column_hash = {}
        for i in range(self.t_table.ncols):
            column_hash[self.t_table.cell_value(0, i)] = i
        return column_hash

    def col_field(self):
        column_hash = {}
        for i in range(self.t_table.ncols):
            column_hash[self.t_table.cell_value(0, i)] = i
        return column_hash

    def f_v_dict(self,f_index):
        f_v_list = []
        f_v_dict = {}
        for i in range(1, self.t_table.nrows):
            f_v_list.append(self.t_table.cell_value(i, self.col_field()[f_index]))
            f_v_dict[f_index] = f_v_list
        return f_v_dict

    def f_v_k_dict(self,f_index,no_indexs=[]):
        k_v_k_dict = {}
        ifmulti = {}
        # 初始化模块出现次数字典
        for i in range(1,self.t_table.nrows):
            ifmulti[self.t_table.cell_value(i, self.col_field()[f_index])] = 0
        for i in range(1,self.t_table.nrows):
            f_vk_dict = {}
            if ifmulti[self.t_table.cell_value(i, self.col_field()[f_index])] != 0:    #判断模块是否第一次循环，模块字典列表取值
                f_vk_list = k_v_k_dict[self.t_table.cell_value(i, self.col_field()[f_index])]
            else:
                f_vk_list = []
            for n in range(self.t_table.ncols):
                noinlist = [self.col_field()[f_index]]
                # 判断排除列表
                if no_indexs:
                    for no_index in no_indexs:
                        noinlist.append(self.col_field()[no_index])
                if n not in noinlist: # 排除列表
                    if self.t_table.cell_value(i,n):   #单元格是否为空
                        f_vk_dict[self.t_table.cell_value(0, n)] = self.t_table.cell_value(i, n)
                    else:
                        #值为空即为合并单元格，倒叙循环到前面有值的行
                        for m in range(i,1,-1):
                            if self.t_table.cell_value(m,n):
                                f_vk_dict[self.t_table.cell_value(0, n)] = self.t_table.cell_value(m, n)
                                break
            f_vk_list.append(f_vk_dict)
            ifmulti[self.t_table.cell_value(i, self.col_field()[f_index])] += 1
            k_v_k_dict[self.t_table.cell_value(i, self.col_field()[f_index])]=f_vk_list
        return k_v_k_dict



class Ex_inventory(object):

    def __init__(self,filename,t_name):
        self.intable = Ex_table(filename=filename,t_name=t_name)
        self._groups = self.intable.f_v_dict('appname')['appname']
        self._hosts = self.intable.f_v_dict('ip')['ip']
    
    def groupvarslist(self,k_index='',no_indexs=[]):
        groupvarlistdict = {}
        if k_index:
            groupvarlistdict[k_index] = self.intable.f_v_k_dict('appname', no_indexs)[k_index]
        else:
            for group in self._groups:
                groupvarlistdict[group] = self.intable.f_v_k_dict('appname',no_indexs)[group]
        ###重新生成group的hostlist和groupvardict
        groupdict = {}
        for group in groupvarlistdict:
            hostlist = []
            groupvarsdict = {}
            group_h_v_dict = {'hosts': [], 'vars': {}}
            ###生成var字典
            for var in groupvarlistdict[group]:
                hostlist.append(var['ip'])
                group_h_v_dict['hosts'] =hostlist
                var_notin=['ip','ansible_ssh_user','ansible_ssh_pass']
                for key in var.keys():
                    if key not in var_notin:
                        groupvarsdict[key] = var[key]
                group_h_v_dict['vars'] = groupvarsdict
            groupdict[group] = group_h_v_dict
        return groupdict

    def hostvarslist(self,k_index='',no_indexs=[]):
            if no_indexs:
                no_indexs = no_indexs
            else:
                no_indexs = ['project','version','deploypath','appname']
            vardict_in_ex = self.intable.f_v_k_dict('ip', no_indexs)
            hostvardict = {}
            for host in self._hosts:
                vardict = {'hostvars': {}}
                for var in vardict_in_ex[host]:
                    for key in var.keys():
                        vardict['hostvars'][key] = var[key]
                hostvardict[host] = vardict
            return (hostvardict)

if __name__ == "__main__":
    filename = '/home/dami/JenkinsHome/workspace/builds/releaseconfig/BBST.xlsx'
    sheetname = 'huaweiyunUAT'
    exinventory = Ex_inventory(filename, sheetname)
    if len(sys.argv) == 2 and (sys.argv[1] in ['--list','-l']):
        print(json.dumps(exinventory.groupvarslist(), indent=4))
    elif len(sys.argv) == 2 and (sys.argv[1] in ['--init', '-i']):
        cmd = "ansible -i exceltable.py all -m ping"
        subprocess.check_call(cmd, shell=True)
        hostslist = exinventory._hosts
        for host in hostslist:
            username = exinventory.hostvarslist()[host]['hostvars']['ansible_ssh_user']
            password = exinventory.hostvarslist()[host]['hostvars']['ansible_ssh_pass']
            cmd = "sshpass -p " + password + " rsync -avz /home/" + username + "/.ssh/id_rsa.pub " \
                  + username + "@" + host + ":/home/" + username + "/.ssh/authorized_keys"
            subprocess.check_call(cmd, shell=True)
    elif len(sys.argv) == 3 and (sys.argv[1] in ['--list','-l']):
        groupname = sys.argv[2]
        print(json.dumps(exinventory.groupvarslist()[groupname], indent=4))
    elif len(sys.argv) == 3 and (sys.argv[1] == '--host'):
        hostname = sys.argv[2]
        print(json.dumps(exinventory.hostvarslist()[hostname]['hostvars'],indent=4))
    elif len(sys.argv) == 3 and (sys.argv[1] in ['--assort','-a']):
        groupname = sys.argv[2]
        deploypath = exinventory.groupvarslist()[groupname]['vars']['deploypath']
        for i in deploypath.split('/'):
            pattern = r'tomcat'
            matchre = re.search(pattern, deploypath)
            if matchre:
                apptype=[i,sheetname]
            else:
                apptype=['java',sheetname]
        print(apptype[0],apptype[1])
    elif len(sys.argv) == 2 and (sys.argv[1] in ['-h','--help']):
        sys.stdout.write('''-l or --list  展示inventory all,
                        --i or --init  导入证书认证
                        -l or --list + groupname  展示host和groupvars,
                        --host + hostname  展示hostvars,
                        -h or --help  帮助信息''')