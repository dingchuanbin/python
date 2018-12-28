#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:ding

from exceltable import Exceldb,Ex_table
import sys
exceltable=Ex_table('BBST.xlsx','Test')
procolnum=exceltable.col_field()['project']
vercolnum=exceltable.col_field()['version']
proversiondict={}
for i in range(1,exceltable.t_table.nrows):
    proname=exceltable.t_table.cell_value(i, procolnum).lower()
    proversion=exceltable.t_table.cell_value(i, vercolnum)
    if  proname != '':
        proversiondict[proname]=proversion
print(proversiondict[sys.argv[1]])


