#!/usr/bin/env python
#-*- coding:utf-8 -*-
import json
import time
import socket



def main():
    endpoint = socket.gethostname()
    timestamp = int(time.time())
    data = [{"endpoint": endpoint, "tags": "test", "timestamp": timestamp,
         "metric": "focus.test", "value": 12,
         "counterType": "GAUGE", "step": 60}]
    print json.dumps(data)
    
if __name__ == '__main__':
    main()
