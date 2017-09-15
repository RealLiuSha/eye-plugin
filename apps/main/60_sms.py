#!/usr/bin/env python
# coding=utf-8
# Create By Freedie.liu
from __future__ import print_function
from __future__ import unicode_literals

import re
import json
import socket
from time import time as timestamp

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

EMEI_ADDR = "https://sms.253.com/msg/balance/json"
EMEI_CONF = {
    "account": "",
    "password": ""
}

CHUANGLAN_ADDR = "http://sdk999ws.eucp.b2m.cn:8080/sdkproxy/querybalance.action?cdkey={cdkey}&password={password}"
CHUANGLAN_CONF = {
    "cdkey": "",
    "password": ""
}


def get_emei_margin_metric():
    r = urllib2.Request(EMEI_ADDR, data=json.dumps(EMEI_CONF), headers={"Content-type": "application/json"})
    try:
        balance = json.loads(urllib2.urlopen(r).read().decode('utf8'))["balance"]
        return {
            "endpoint": socket.gethostname(),
            "metric": "emei_margin",
            "timestamp": int(timestamp()),
            "step": 60,
            "value": balance,
            "counterType": "GAUGE",
            "tags": "type=plugin,app=sms"
        }
    except Exception:
        return {}


def get_chuanglan_margin_metric():
    try:
        r = urllib2.urlopen(CHUANGLAN_ADDR.format(**CHUANGLAN_CONF)).read().decode('utf8')
        m = re.search("<message>(.*)</message>", r)
        return {
            "endpoint": socket.gethostname(),
            "metric": "chuanglan_margin",
            "timestamp": int(timestamp()),
            "step": 60,
            "value": m.groups()[0],
            "counterType": "GAUGE",
            "tags": "type=plugin,app=sms"
        }
    except Exception:
        return {}


def main(metrics=[]):
    metrics.append(get_chuanglan_margin_metric())
    metrics.append(get_emei_margin_metric())

    return metrics


if __name__ == '__main__':
    print(main())
