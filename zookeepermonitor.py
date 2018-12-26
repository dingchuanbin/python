#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
from kazoo.client import KazooClient

def monitor():
    try:
        nodePath = "/quotation/lines/NEURCNH"
        host = "47.92.168.183"
        port = "8011"
        timeout = 100
        zkcn = KazooClient(hosts=host + ':' + port,timeout=timeout)
        zkcn.start()
        nodevalue = zkcn.get(nodePath)

        # nodevaluedict = ast.literal_eval(bytes.decode(nodevalue[0]))
        print(nodevalue)
        zkcn.stop()
        zkcn.close()
    except Exception as e:
        print(str(e))
monitor()