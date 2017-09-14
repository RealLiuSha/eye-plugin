#!/usr/bin/env python
# coding=utf-8
# Create By Freedie.liu
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import json
import socket

from time import time as timestamp
from subprocess import PIPE, Popen, STDOUT

JMX_ADDR = "127.0.0.1:12345"

JMX_CLIENT_PATH = "../../libs"

METRICS = {
    "java.lang:type=ClassLoading": [
        {"类-已卸载": "UnloadedClassCount"},
        {"类-已加载": "LoadedClassCount"},
        {"类-总计": "TotalLoadedClassCount"}
    ],
    "Catalina:type=ThreadPool,name=\"http-nio-8080\"": [
        {"线程-CurrentThreadsBusy": "currentThreadsBusy"}
    ],
    "java.lang:type=Memory": [
        {"堆内存最大": "HeapMemoryUsage.max"},
        {"堆内存已使用": "HeapMemoryUsage.used"},
        {"堆内存已提交": "HeapMemoryUsage.committed"}
    ],
    "java.lang:type=Threading": [
        {"活动线程": "ThreadCount"},
        {"线程峰值": "PeakThreadCount"},
        {"线程总计": "TotalStartedThreadCount"}
    ]
}

PATH = os.path.dirname(os.path.realpath(__file__))
DEBUG = (sys.argv[-1].lower() == 'debug') if len(sys.argv) > 0 else False


def generate_metric_script():
    return '\n'.join([
        'get -n -b {0} {1}'.format(object_name, list(attribute.values()).pop())
        for object_name, attributes in METRICS.items()
        for attribute in attributes if len(attribute) > 0
    ])


def get_jmx_metric():
    if not os.path.exists(os.path.join(PATH, JMX_CLIENT_PATH)):
        return [{}]

    command = "/bin/bash -c \"echo '{script}' | java -jar {command_path} -l {host} -v silent -n\"".format(**{
        "script": generate_metric_script(),
        "command_path": os.path.join(PATH, JMX_CLIENT_PATH, "jmxclient.jar"),
        "host": JMX_ADDR,
    })

    process = Popen(command, stdout=PIPE, shell=True, universal_newlines=True, stderr=STDOUT)
    result, _ = process.communicate()
    status = process.poll()

    if result[-1:] == '\n': result = result[:-1]

    split_sep = ' = '

    def generate_metric(_str):
        data = _str.split(split_sep)
        return {
            "endpoint": socket.gethostname(),
            "metric": data[0],
            "timestamp": int(timestamp()),
            "step": 60,
            "value": data[1].replace(";", ""),
            "counterType": "GAUGE",
            "tags": "type=plugin,app=%s" % PATH.split('/')[-1]
        }

    return [{}] if status != 0 else [
        generate_metric(str_line)
        for str_line in filter(None, result.split('\n')) if split_sep in str_line
    ]


def main():
    payload = get_jmx_metric()
    print(json.dumps(payload).encode('utf8'))


if __name__ == '__main__':
    # noinspection PyBroadException
    try:
        main()
    except Exception:
        pass
