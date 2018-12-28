#!/usr/bin/env python
#-*- coding:utf-8 -*-
#author:ding

from ansible.plugins.callback.default import CallbackModule
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from collections import namedtuple
import os

class AnsibleTask:
    def __init__(self,invent_file,extra_vars={},tagslist=[]):
        self.invent_file = invent_file
        self.passwords = None
        self.result_callback = CallbackModule()
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
                stdout_callback = self.result_callback,
            )
            taskqm.run(play)
            return self.result_callback
        except:
            raise
        finally:
            if taskqm is not None:
                taskqm.cleanup()

    def exec_playbook(self,playbooks):
        playbook = PlaybookExecutor(playbooks=playbooks,inventory=self.inventory,
                                    variable_manager=self.variable_manager,loader=self.loader,
                                    options=self.options,passwords=self.passwords)
        setattr(getattr(playbook,'_tqm'),'_stdout_callback',self.result_callback)
        playbook.run()
        return self.result_callback


inventory_file = './exceltable.py'
deployapps='marginservice traderisk exchange bst_admin legaltrade'
deployapps=deployapps.split(' ')
# javaapplist=[]
# webapplist=[]
for deployapp in deployapps:
    g_assert = os.popen('python ' + inventory_file + ' -a '+deployapp)
    g_assert = g_assert.read()
    if g_assert:
        extra_vars = {'hostname': deployapp}
        playbookfile = ['test.yml']
        tagslist = []
        task = AnsibleTask(inventory_file, extra_vars, tagslist)
        task.exec_playbook(playbookfile)
    else:
        extra_vars = {'hostname': deployapp}
        playbookfile = ['test.yml']
        tagslist = []
        task = AnsibleTask(inventory_file, extra_vars, tagslist)
        task.exec_playbook(playbookfile)

# if javaapplist:
#     extra_vars = {'hostname': javaapplist}
#     playbookfile = ['test.yml']
#     tagslist = []
#     task = AnsibleTask(inventory_file, extra_vars, tagslist)
#     task.exec_playbook(playbookfile)
# if webapplist:
#     extra_vars = {'hostname': webapplist}
#     playbookfile = ['test.yml']
#     tagslist = []
#     task = AnsibleTask(inventory_file, extra_vars, tagslist)
#     task.exec_playbook(playbookfile)


