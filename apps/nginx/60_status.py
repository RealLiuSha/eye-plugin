#!/usr/bin/env python
# coding=utf-8
# Create By Freedie.liu
from __future__ import print_function
from __future__ import unicode_literals

import os
import re
import sys
import json
import socket
from time import time as timestamp

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2


NGX_ADDR = "127.0.0.1:8081"

PATH = os.path.dirname(os.path.realpath(__file__))


# noinspection PyBroadException
def get_ngx_metrics():
    try:
        nginx_status_conn = urllib2.urlopen("http://%s/nginx_status" % NGX_ADDR)
        nginx_status_data = nginx_status_conn.read().decode('utf8')
    except urllib2.URLError:
        print('status err URLError: check the URL and that Nginx running.')
        sys.exit(127)
    except Exception:
        print('status err failed to obtain nginx status metrics.')
        sys.exit(127)

    req_active = re.search(r'Active connections:\s+(\d+)', nginx_status_data).group
    req_conn_stats = re.search(r'\s*(\d+)\s+(\d+)\s+(\d+)', nginx_status_data).group
    req_io_stats = re.search(r'Reading:\s*(\d+)\s*Writing:\s*(\d+)\s*Waiting:\s*(\d+)', nginx_status_data).group

    try:
        return [
            {
                "endpoint": socket.gethostname(),
                "metric": key,
                "timestamp": int(timestamp()),
                "step": 60,
                "value": value,
                "counterType": "GAUGE",
                "tags": "type=plugin,app=%s" % PATH.split('/')[-1]
            }
            for key, value in {
                "active_connections": req_active(1),
                "accepted_connections": req_conn_stats(1),
                "handled_connections": req_conn_stats(2),
                "number_of_requests": req_conn_stats(3),
                "connections_reading": req_io_stats(1),
                "connections_writing": req_io_stats(2),
                "connections_waiting": req_io_stats(3)
            }.items()
        ]
    except IndexError:
        return {}


def main():
    print(json.dumps(get_ngx_metrics()))


if __name__ == '__main__':
    main()
