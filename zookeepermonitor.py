#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
from kazoo.client import KazooClient

def main():
    try:
        nodePath = "/quotation/lines/NEURCNH"
        hosts="47.92.168.183:8011"
        timeout = 100
        zkcn = KazooClient(hosts=hosts,timeout=timeout)
        zkcn.start()
        nodevalue = zkcn.get(nodePath)
        # nodevaluedict = ast.literal_eval(bytes.decode(nodevalue[0]))
        print(nodevalue)
        zkcn.stop()
        zkcn.close()
    except Exception as e:
        print(str(e))
main()