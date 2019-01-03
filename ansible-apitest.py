#!/usr/bin/env python
#-*- coding:utf-8 -*-
#author:ding

from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from collections import namedtuple
import sys
import subprocess

import os

class AnsibleTask:
    def __init__(self,invent_file,extra_vars={},tagslist=[]):
        self.invent_file = invent_file
        self.passwords = None
        Options = namedtuple('Options',
                             ['connection',
                              'remote_user',
                              'ask_sudo_pass',
                              'verbosity',
                              'ack_pass',
                              'module_path',
                              'forks',
                              'become',
                              'become_method',
                              'become_user',
                              'check',
                              'host_key_checking',
                              'listhosts',
                              'listtasks',
                              'listtags',
                              'syntax',
                              'sudo_user',
                              'sudo',
                              'diff',
                              'tags',
                              'display_skipped_hosts'
                              ])
        self.options = Options(connection='smart',
                          remote_user=None,
                          ack_pass=None,
                          sudo_user=None,
                          forks=10,
                          sudo=None,
                          ask_sudo_pass=False,
                          verbosity=10,
                          module_path=None,
                          become=None,
                          become_method=None,
                          become_user=None,
                          check=False,
                          diff=False,
                          host_key_checking=False,
                          listhosts=None,
                          listtasks=None,
                          listtags=None,
                          syntax=None,
                          tags=tagslist,
                          display_skipped_hosts=True
                          )
        #实例化解析yml
        self.loader = DataLoader()
        #实例化资产管理
        self.inventory = InventoryManager(loader=self.loader,sources=invent_file)
        #实例化变量管理
        self.variable_manager = VariableManager(loader=self.loader,inventory=self.inventory)
        if extra_vars:
            self.variable_manager.extra_vars = extra_vars

    def exec_shell(self,hostlist=[],command=None):
        source = {'hosts': hostlist, 'gather_facts': 'no', 'tasks': [
            {'action': {'module': 'shell', 'args': command}, 'register': 'shell_out'}]}
        play = Play().load(source, variable_manager=self.variable_manager, loader=self.loader)

        try:
            taskqm = TaskQueueManager(
                inventory = self.inventory,
                variable_manager = self.variable_manager,
                loader = self.loader,
                options = self.options,
                passwords = self.passwords,
                # stdout_callback = self.result_callback,
            )
            taskqm.run(play)
        except:
            raise
        finally:
            if taskqm is not None:
                taskqm.cleanup()

    def exec_playbook(self,playbooks):
        pbex = PlaybookExecutor(playbooks=playbooks,inventory=self.inventory,
                                    variable_manager=self.variable_manager,loader=self.loader,
                                    options=self.options,passwords=self.passwords)
        results=pbex.run()


if __name__ == "__main__":
    inventory_file = './exceltable.py'
    deployapps=sys.argv[1]
    tagslist=sys.argv[2]
    deployapps=deployapps.split(',')
    tagslist=tagslist.split(',')
    for deployapp in deployapps:
        g_assert = os.popen('python ' + inventory_file + ' -a '+deployapp)
        g_assert = str(g_assert.read()).strip().split(' ')
        s_dir = '../builds/releasebuilds/' + g_assert[1] + '/' + deployapp
        c_dir = '../builds/releasebuilds/' + g_assert[1] + '_config/' + deployapp
        if g_assert[0] == 'java':
            if 'deploy' in tagslist or 'config' in tagslist:
                cmd = "rsync -avrz --delete %s roles/javaapps/files/" % (s_dir)
                subprocess.check_call(cmd, shell=True)
                if os.path.exists(c_dir):
                    cmd = "rsync -avrz --delete %s roles/javaapps/templates/" % (c_dir)
                    subprocess.check_call(cmd, shell=True)
            extra_vars = {'hostname': deployapp,'rolename':deployapp}
            playbookfile = ['javaapps.yml']
            task = AnsibleTask(inventory_file, extra_vars, tagslist)
            task.exec_playbook(playbookfile)
        else:
            if 'deploy' in tagslist or 'config' in tagslist:
                cmd = "rsync -avrz --delete %s roles/webapps/files/" % (s_dir)
                subprocess.check_call(cmd, shell=True)
                if os.path.exists(c_dir):
                    cmd = "rsync -avrz --delete %s roles/webapps/templates/" % (c_dir)
                    subprocess.check_call(cmd, shell=True)
            extra_vars = {'hostname': deployapp,'deploypath':g_assert[0],'rolename':deployapp}
            playbookfile = ['webapps.yml']

            task = AnsibleTask(inventory_file, extra_vars, tagslist)
            task.exec_playbook(playbookfile)
