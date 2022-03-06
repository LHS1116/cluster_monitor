# -*- coding: utf-8 -*-
""" 
@Describe: 
@Time    : 2022/1/19 5:06 下午
@Author  : liuhuangshan
@File    : utils.py
"""
import datetime
import json
import random
import threading
import time
import requests
import redis
from typing import List, Dict, Union

from itsdangerous import TimedSerializer, TimestampSigner

from models import SlurmJob, SlurmNode, SlurmPartition, SlurmAlertInfo

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
UPDATE_DELTA = 15
sec_key = "w183$sjOv&"
serializer = TimedSerializer(sec_key)
signer = TimestampSigner(sec_key)
redis_cli = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def get_response(data: Union[Dict, List], code: int):
    return {
        'code': code,
        'message': 'ok',
        'data': data,
    }


def cal_timedelta(start: datetime, end: datetime) -> str:
    if not start or not end:
        return ''
    seconds = int((end - start).total_seconds())
    days = int(seconds / (3600 * 24))
    seconds %= (3600 * 24)
    hours = int(seconds / 3600)
    seconds %= 3600
    minutes = int(seconds / 60)
    seconds %= 60
    seconds = round(seconds, 2)
    res = ''
    if days:
        res += f'{days} d '
    if hours:
        res += f'{hours} h '
    if minutes:
        res += f'{minutes} m '
    res += f'{seconds} s'
    return res


def transfer_time(time_str):
    if not time_str:
        return None
    return datetime.datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")



def format_data(data: str):
    lines = data.split('\n')
    res = []
    if len(lines) == 1:
        return lines
    names = lines[0].split()
    values = lines[1:]
    for v in values:
        _v = v.split()
        res.append(dict(zip(names, _v)))
    return res
    # print(res)


def generate_token(value: str):
    try:
        t = signer.sign(value)
        return t
    except Exception as e:
        print(e)
        return ''


def verify_token(token) -> bool:
    """验证token有效性"""
    try:
        if isinstance(token, str):
            token = bytes(token, 'utf-8')
        assert isinstance(token, bytes)
        r = signer.unsign(token, 60)
        print(r)
        return True
    except Exception as e:
        print(e)
        return False



def get_today_jobs() -> List[SlurmJob]:
    return []

def get_slurm_nodes(node_id: int = None, node_name: str = None) -> List[SlurmNode]:
    nodes = redis_cli.get('nodes')
    if not nodes:
        return []
    return json.loads(nodes)


def get_slurm_jobs(return_all: bool = False, return_dict: bool = False) -> List[Dict]:
    """获取作业列表"""
    jobs = redis_cli.get('jobs')
    if not jobs:
        return []
    jobs = json.loads(jobs)

    for job in jobs:
        key = f'slurm_job_{job["job_id"]}'
        val = redis_cli.get(key)
        ave_cpu = job.get('ave_cpu', 0)
        ave_gpu = job.get('ave_gpu', 0)

        if not val:
            job['cpu_utilization'] = 0
        else:
            val = json.loads(val)
            job['cpu_utilization'] = (ave_cpu - val['ave_cpu']) / UPDATE_DELTA

        val = {'ave_cpu': ave_cpu, 'ave_gpu': ave_gpu}
        redis_cli.set(key, json.dumps(val))
    return jobs


def get_slurm_partition() -> Dict:
    # TODO
    example = {
        'cpu': {
            'nodes': [{'name': f'cpu_{i}', 'state': 'DOWN'} for i in range(4)],
            'total_gpus': 1320,
            'total_cpus': 897,
            'running_jobs': 0,
            'state': 'DOWN',
            'default': 1
        },
        'dell': {
            'nodes': [{'name': f'dell_{i}', 'state': 'UP'} for i in range(8)],
            'total_gpus': 320,
            'total_cpus': 97,
            'running_jobs': 13,

            'state': 'UP',
            'default': 1
        },
        'sugon': {
            'nodes': [{'name': f'sougon_{i}', 'state': 'DRAIN'} for i in range(6)],
            'total_gpus': 473,
            'total_cpus': 199,
            'running_jobs': 6,
            'state': 'DRAIN',
            'default': 1
        }
    }
    parts = redis_cli.get('partitions')
    if parts:
        parts = json.loads(parts)
    else:
        parts = []
    res = {}
    job_counts = {}
    jobs = redis_cli.get('jobs')
    if jobs:
        jobs = json.loads(jobs)
    else:
        jobs = []
    for job in jobs:
        part = job['partition']
        count = job_counts.get(part, 0) + 1
        job_counts[part] = count

    for partition in parts:
        res[partition['name']] = {
            'nodes': partition['nodes'],
            'total_gpu': partition['total_gpu'],
            'total_cpu': partition['total_cpu'],
            'running_jobs': job_counts.get(partition['name'], 0),
            'state': partition['state'],
            'default': partition['default']
        }
    return res


def get_slurm_user_utilization_by_time():
    pass

def get_user_resource():
    return {}
def get_slurm_partition_utilization_by_time():
    # TODO:
    now = datetime.datetime.now()
    return []


def do_upload_data(data: dict):
    assert isinstance(data, dict), 'wrong format!'
    for k in data:
        json_str = json.dumps(data[k])
        redis_cli.set(k, json_str, ex=3600 * 48)
    for k in data:
        print(k, json.loads(redis_cli.get(k)))
        print('=' * 30)


def do_record_alert():
    pass


def get_cancel_job() -> List:
    return []

def solve_alert(alert_info):
    """处理报警信息"""
    example = {
        'receiver': 'email_and_webhook',
        'status': 'firing',
        'alerts': [
            {
                'status': 'firing',
                'labels': {
                    'alertname': 'clusterNodeStatesAlert',
                    'instance': 'localhost:8080',
                    'job': 'slurm_exporter',
                    'severity': 'page',
                    'user': 'root'
                },
                'annotations': {
                    'description': '实例localhost:8080 缺少可用节点  (当前值为: 0)',
                    'summary': '集群无可用节点报警 localhost:8080'
                },
                'startsAt': '2022-03-03T11:58:24.943Z',
                'endsAt': '0001-01-01T00:00:00Z',
                'generatorURL': 'http://lhs-01:9090/graph?g0.expr=slurm_nodes_idle+%3D%3D+0&g0.tab=1',
                'fingerprint': '66c453b94b4abf47'
            }
        ],
        'groupLabels': {'alertname': 'clusterNodeStatesAlert'},
        'commonLabels': {
            'alertname': 'clusterNodeStatesAlert',
            'instance': 'localhost:8080',
            'job': 'slurm_exporter',
            'severity': 'page',
            'user': 'root'
        },
        'commonAnnotations': {'description': '实例localhost:8080 缺少可用节点  (当前值为: 0)',
                              'summary': '集群无可用节点报警 localhost:8080'},
        'externalURL': 'http://lhs-01:90',
        'groupKey': '{}:{alertname="clusterNodeStatesAlert"}',
        'truncatedAlerts': 0}
    now = datetime.datetime.now()
    key = f'alert_{now.strftime("%Y-%m-%d")}'
    today_alerts = redis_cli.get(key)
    if today_alerts is None:
        today_alerts = {}
    else:
        today_alerts = json.loads(today_alerts)

    alerts = alert_info.get('alerts')

    for alert in alerts:
        _alert = SlurmAlertInfo()
        _alert.start_at = alert['startsAt']
        _alert.end_at = alert['endsAt']
        _alert.title = alert['annotations']['summary']
        _alert.description = alert['annotations']['description']
        _alert.alert_name = alert['labels']['alertname']
        _alert.user = alert['labels']['user']
        _alert.node = alert['labels']['instance']
        tmp = today_alerts.get(_alert.alert_name, [])
        tmp.append(_alert.__dict__)
        today_alerts[_alert.alert_name] = tmp
    redis_cli.set(key, json.dumps(today_alerts), ex=3600 * 24)




def do_update_canceled_job(job_id: List):
    if job_id:
        cancel_list = redis_cli.get('cancel_list')
        if cancel_list:
            cancel_list = json.loads(cancel_list)
            tmp = []
            for jid in cancel_list:
                if jid not in job_id:
                    tmp.append(jid)
            redis_cli.set('cancel_list', json.dumps(tmp))


def update_canceled_job(job_id: List):
    threading.Thread(target=do_upload_data, args=job_id).start()


def test():
    url = 'http://0.0.0.0:8000/alert/create'
    data = {
        'total_gpu_info': {'rtx6k': 3, 'v100': 2, 'm40': 3, 'p40': 4},
        'accessible_gpu_info': {'rtx6k': 1, 'v100': 2, 'm40': 3, 'p40': 4},
        'user_usage_info': {'user1': 1, 'user2': 1, 'user3': 3},
        'available_gpu_info': {'p40': 0, 'rtx6k': 1, 'v100': 2, 'm40': 2}
    }
    resp = requests.post(url, data=data)
    print(resp.content)


# print(type(dumps_data()))

def test_redis():
    data = {"current_user": ['root'], "gpu_stat": {"accessible_gpu_info": {"m40": 3, "p40": 4, "rtx6k": 1, "v100": 2},
                                                   "available_gpu_info": {"m40": 2, "p40": 0, "rtx6k": 1, "v100": 2},
                                                   "total_gpu_info": {"m40": 3, "p40": 4, "rtx6k": 3, "v100": 2},
                                                   "user_usage_info": {"user1": 1, "user2": 1, "user3": 3}}, "jobs": [
        {"AveRSS": "", "End": "2021-12-28T02:03:10", "JobID": "2", "JobName": "hostname", "QOS": "", "ReqCPUS": "4",
         "ReqTRES": "", "Start": "2021-12-28T02:03:10", "State": "CANCELLED", "Submit": "2021-12-28T02:02:54",
         "User": "root"},
        {"AveRSS": "", "End": "2021-12-28T02:23:51", "JobID": "3", "JobName": "hostname", "QOS": "", "ReqCPUS": "0",
         "ReqTRES": "", "Start": "2021-12-28T02:23:51", "State": "CANCELLED", "Submit": "2021-12-28T02:03:13",
         "User": "root"},
        {"AveRSS": "", "End": "2021-12-28T02:43:14", "JobID": "4", "JobName": "hostname", "QOS": "", "ReqCPUS": "0",
         "ReqTRES": "", "Start": "2021-12-28T02:43:14", "State": "CANCELLED", "Submit": "2021-12-28T02:42:37",
         "User": "root"},
        {"AveRSS": "856K", "End": "2021-12-28T02:43:17", "JobID": "5", "JobName": "hostname", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2021-12-28T02:43:17", "State": "COMPLETED", "Submit": "2021-12-28T02:43:17",
         "User": "root"},
        {"AveRSS": "860K", "End": "2021-12-28T02:43:21", "JobID": "6", "JobName": "hostname", "QOS": "", "ReqCPUS": "4",
         "ReqTRES": "", "Start": "2021-12-28T02:43:21", "State": "COMPLETED", "Submit": "2021-12-28T02:43:21",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-21T23:11:07", "JobID": "7", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "4",
         "ReqTRES": "", "Start": "2022-02-21T23:11:07", "State": "CANCELLED", "Submit": "2022-02-21T22:15:01",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-21T23:11:11", "JobID": "8", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "4",
         "ReqTRES": "", "Start": "2022-02-21T23:11:11", "State": "CANCELLED", "Submit": "2022-02-21T22:15:21",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-21T23:22:07", "JobID": "9", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-21T23:22:05", "State": "NODE_FAIL", "Submit": "2022-02-21T22:15:49",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-21T23:50:12", "JobID": "10", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-21T23:50:10", "State": "NODE_FAIL", "Submit": "2022-02-21T22:54:56",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-21T23:10:36", "JobID": "11", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-21T23:10:36", "State": "CANCELLED", "Submit": "2022-02-21T23:10:36",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-21T23:15:39", "JobID": "12", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-21T23:15:39", "State": "CANCELLED", "Submit": "2022-02-21T23:10:49",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-21T23:19:22", "JobID": "13", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-21T23:19:22", "State": "CANCELLED", "Submit": "2022-02-21T23:16:18",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-21T23:19:53", "JobID": "14", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-21T23:19:53", "State": "CANCELLED", "Submit": "2022-02-21T23:19:34",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-21T23:56:02", "JobID": "15", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-21T23:56:02", "State": "CANCELLED", "Submit": "2022-02-21T23:56:02",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-21T23:56:24", "JobID": "16", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-21T23:56:24", "State": "CANCELLED", "Submit": "2022-02-21T23:56:24",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-21T23:59:01", "JobID": "17", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-21T23:59:01", "State": "CANCELLED", "Submit": "2022-02-21T23:58:13",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-22T00:04:58", "JobID": "18", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-22T00:04:58", "State": "CANCELLED", "Submit": "2022-02-21T23:59:28",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-22T00:05:36", "JobID": "19", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-22T00:05:36", "State": "CANCELLED", "Submit": "2022-02-22T00:05:36",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-22T04:03:07", "JobID": "20", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-22T04:03:07", "State": "CANCELLED", "Submit": "2022-02-22T04:03:07",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-22T04:19:28", "JobID": "21", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-22T04:19:28", "State": "CANCELLED", "Submit": "2022-02-22T04:19:28",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-22T19:50:23", "JobID": "22", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-22T19:50:23", "State": "FAILED", "Submit": "2022-02-22T19:50:23",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-22T19:50:58", "JobID": "23", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-22T19:50:56", "State": "NODE_FAIL", "Submit": "2022-02-22T19:50:56",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-23T01:13:02", "JobID": "24", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-23T01:13:02", "State": "CANCELLED", "Submit": "2022-02-22T19:55:51",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-23T01:06:49", "JobID": "25", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-23T01:06:49", "State": "CANCELLED", "Submit": "2022-02-22T19:57:09",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-23T01:10:48", "JobID": "26", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-23T01:10:48", "State": "CANCELLED", "Submit": "2022-02-23T01:10:48",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-23T01:11:22", "JobID": "27", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-23T01:11:22", "State": "CANCELLED", "Submit": "2022-02-23T01:11:16",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-23T01:11:29", "JobID": "28", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-23T01:11:29", "State": "CANCELLED", "Submit": "2022-02-23T01:11:24",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-23T01:11:32", "JobID": "29", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-23T01:11:32", "State": "CANCELLED", "Submit": "2022-02-23T01:11:30",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-23T01:12:22", "JobID": "30", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "0",
         "ReqTRES": "", "Start": "2022-02-23T01:12:22", "State": "FAILED", "Submit": "2022-02-23T01:12:22",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-23T01:12:45", "JobID": "31", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "0",
         "ReqTRES": "", "Start": "2022-02-23T01:12:45", "State": "FAILED", "Submit": "2022-02-23T01:12:45",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-23T01:15:53", "JobID": "32", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "0",
         "ReqTRES": "", "Start": "2022-02-23T01:15:53", "State": "FAILED", "Submit": "2022-02-23T01:15:53",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-23T01:20:39", "JobID": "33", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-23T01:20:39", "State": "FAILED", "Submit": "2022-02-23T01:20:39",
         "User": "root"},
        {"AveRSS": "868K", "End": "2022-02-23T01:24:39", "JobID": "34", "JobName": "testslurm+", "QOS": "",
         "ReqCPUS": "2", "ReqTRES": "", "Start": "2022-02-23T01:24:39", "State": "FAILED",
         "Submit": "2022-02-23T01:24:39", "User": "root"},
        {"AveRSS": "864K", "End": "2022-02-23T01:24:50", "JobID": "35", "JobName": "testslurm+", "QOS": "",
         "ReqCPUS": "2", "ReqTRES": "", "Start": "2022-02-23T01:24:50", "State": "FAILED",
         "Submit": "2022-02-23T01:24:50", "User": "root"},
        {"AveRSS": "860K", "End": "2022-02-23T01:24:57", "JobID": "36", "JobName": "testslurm+", "QOS": "",
         "ReqCPUS": "2", "ReqTRES": "", "Start": "2022-02-23T01:24:57", "State": "FAILED",
         "Submit": "2022-02-23T01:24:57", "User": "root"},
        {"AveRSS": "868K", "End": "2022-02-23T01:27:35", "JobID": "37", "JobName": "testslurm+", "QOS": "",
         "ReqCPUS": "2", "ReqTRES": "", "Start": "2022-02-23T01:27:35", "State": "COMPLETED",
         "Submit": "2022-02-23T01:27:35", "User": "root"},
        {"AveRSS": "864K", "End": "2022-02-23T01:27:54", "JobID": "38", "JobName": "testslurm+", "QOS": "",
         "ReqCPUS": "2", "ReqTRES": "", "Start": "2022-02-23T01:27:54", "State": "FAILED",
         "Submit": "2022-02-23T01:27:54", "User": "root"},
        {"AveRSS": "", "End": "2022-02-23T01:29:14", "JobID": "39", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-23T01:29:14", "State": "FAILED", "Submit": "2022-02-23T01:29:14",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-23T01:29:39", "JobID": "40", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-23T01:29:39", "State": "COMPLETED", "Submit": "2022-02-23T01:29:39",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-23T01:29:53", "JobID": "41", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-23T01:29:53", "State": "COMPLETED", "Submit": "2022-02-23T01:29:53",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-25T00:47:50", "JobID": "42", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-25T00:37:50", "State": "COMPLETED", "Submit": "2022-02-25T00:37:49",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-25T01:19:28", "JobID": "43", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-25T00:49:27", "State": "COMPLETED", "Submit": "2022-02-25T00:49:27",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-27T18:34:38", "JobID": "44", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-25T01:28:46", "State": "COMPLETED", "Submit": "2022-02-25T01:28:45",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-28T00:06:48", "JobID": "45", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-28T00:06:48", "State": "FAILED", "Submit": "2022-02-28T00:06:48",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-28T03:29:37", "JobID": "46", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "0",
         "ReqTRES": "", "Start": "2022-02-28T03:29:37", "State": "CANCELLED", "Submit": "2022-02-28T00:07:49",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-28T03:29:38", "JobID": "47", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "0",
         "ReqTRES": "", "Start": "2022-02-28T03:29:38", "State": "CANCELLED", "Submit": "2022-02-28T00:10:16",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-28T03:14:34", "JobID": "48", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-28T03:14:02", "State": "COMPLETED", "Submit": "2022-02-28T03:14:02",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-28T03:15:33", "JobID": "49", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-28T03:15:01", "State": "CANCELLED", "Submit": "2022-02-28T03:15:01",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-28T03:29:40", "JobID": "50", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "0",
         "ReqTRES": "", "Start": "2022-02-28T03:29:40", "State": "CANCELLED", "Submit": "2022-02-28T03:16:40",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-28T03:29:16", "JobID": "51", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-28T03:29:16", "State": "FAILED", "Submit": "2022-02-28T03:29:14",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-28T07:10:38", "JobID": "52", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "0",
         "ReqTRES": "", "Start": "2022-02-28T07:10:38", "State": "CANCELLED", "Submit": "2022-02-28T03:32:14",
         "User": "root"},
        {"AveRSS": "", "End": "2022-03-01T02:27:32", "JobID": "53", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "0",
         "ReqTRES": "", "Start": "2022-03-01T02:27:32", "State": "CANCELLED", "Submit": "2022-02-28T03:35:50",
         "User": "root"},
        {"AveRSS": "", "End": "2022-03-01T02:27:33", "JobID": "54", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "0",
         "ReqTRES": "", "Start": "2022-03-01T02:27:33", "State": "CANCELLED", "Submit": "2022-02-28T03:37:16",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-28T03:37:54", "JobID": "55", "JobName": "sq.py", "QOS": "", "ReqCPUS": "2",
         "ReqTRES": "", "Start": "2022-02-28T03:37:22", "State": "COMPLETED", "Submit": "2022-02-28T03:37:22",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-28T04:00:34", "JobID": "56", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-02-28T04:00:34", "State": "FAILED", "Submit": "2022-02-28T04:00:33",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-28T04:00:52", "JobID": "57", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-02-28T04:00:52", "State": "FAILED", "Submit": "2022-02-28T04:00:51",
         "User": "root"},
        {"AveRSS": "864K", "End": "2022-02-28T04:01:51", "JobID": "58", "JobName": "testslurm+", "QOS": "",
         "ReqCPUS": "1", "ReqTRES": "", "Start": "2022-02-28T04:01:51", "State": "COMPLETED",
         "Submit": "2022-02-28T04:01:51", "User": "root"},
        {"AveRSS": "868K", "End": "2022-02-28T04:02:06", "JobID": "59", "JobName": "testslurm+", "QOS": "",
         "ReqCPUS": "1", "ReqTRES": "", "Start": "2022-02-28T04:02:06", "State": "COMPLETED",
         "Submit": "2022-02-28T04:02:06", "User": "root"},
        {"AveRSS": "", "End": "2022-02-28T04:02:36", "JobID": "60", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-02-28T04:02:26", "State": "COMPLETED", "Submit": "2022-02-28T04:02:25",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-28T05:57:22", "JobID": "61", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-02-28T04:03:42", "State": "COMPLETED", "Submit": "2022-02-28T04:03:42",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-28T06:17:13", "JobID": "62", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-02-28T06:00:33", "State": "COMPLETED", "Submit": "2022-02-28T06:00:32",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-28T07:02:27", "JobID": "63", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-02-28T06:45:46", "State": "COMPLETED", "Submit": "2022-02-28T06:45:46",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-28T07:22:32", "JobID": "64", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-02-28T07:05:52", "State": "COMPLETED", "Submit": "2022-02-28T07:05:52",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-28T07:05:54", "JobID": "65", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-02-28T07:05:53", "State": "FAILED", "Submit": "2022-02-28T07:05:53",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-28T07:07:48", "JobID": "66", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-02-28T07:07:48", "State": "FAILED", "Submit": "2022-02-28T07:06:24",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-28T07:39:12", "JobID": "67", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-02-28T07:22:32", "State": "COMPLETED", "Submit": "2022-02-28T07:07:47",
         "User": "root"},
        {"AveRSS": "", "End": "2022-02-28T08:38:57", "JobID": "68", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-02-28T08:22:16", "State": "COMPLETED", "Submit": "2022-02-28T08:22:16",
         "User": "root"},
        {"AveRSS": "", "End": "2022-03-01T04:02:57", "JobID": "69", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-03-01T03:46:16", "State": "COMPLETED", "Submit": "2022-03-01T03:46:16",
         "User": "root"},
        {"AveRSS": "", "End": "2022-03-02T08:28:45", "JobID": "70", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-03-02T08:12:05", "State": "COMPLETED", "Submit": "2022-03-02T08:12:04",
         "User": "root"},
        {"AveRSS": "", "End": "2022-03-02T22:22:48", "JobID": "71", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-03-02T22:06:08", "State": "COMPLETED", "Submit": "2022-03-02T22:06:08",
         "User": "root"},
        {"AveRSS": "", "End": "2022-03-02T22:06:11", "JobID": "72", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-03-02T22:06:11", "State": "FAILED", "Submit": "2022-03-02T22:06:10",
         "User": "root"},
        {"AveRSS": "", "End": "2022-03-02T22:52:11", "JobID": "73", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-03-02T22:35:31", "State": "COMPLETED", "Submit": "2022-03-02T22:35:30",
         "User": "root"},
        {"AveRSS": "", "End": "2022-03-02T23:14:21", "JobID": "74", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-03-02T22:57:41", "State": "COMPLETED", "Submit": "2022-03-02T22:57:41",
         "User": "root"},
        {"AveRSS": "", "End": "2022-03-02T23:35:24", "JobID": "75", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-03-02T23:18:44", "State": "COMPLETED", "Submit": "2022-03-02T23:18:43",
         "User": "root"},
        {"AveRSS": "", "End": "2022-03-03T00:49:23", "JobID": "76", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-03-03T00:32:43", "State": "COMPLETED", "Submit": "2022-03-03T00:32:43",
         "User": "root"},
        {"AveRSS": "", "End": "2022-03-03T01:49:11", "JobID": "77", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-03-03T01:32:31", "State": "COMPLETED", "Submit": "2022-03-03T01:32:30",
         "User": "root"},
        {"AveRSS": "", "End": "2022-03-03T04:54:42", "JobID": "78", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-03-03T03:57:05", "State": "COMPLETED", "Submit": "2022-03-03T03:57:05",
         "User": "root"},
        {"AveRSS": "", "End": "2022-03-03T05:11:22", "JobID": "79", "JobName": "testslurm+", "QOS": "", "ReqCPUS": "1",
         "ReqTRES": "", "Start": "2022-03-03T04:54:42", "State": "COMPLETED", "Submit": "2022-03-03T03:57:06",
         "User": "root"}], "keys": ["gpu_stat", "node_gpu", "current_user", "jobs", "nodes"], "node_gpu": [], "nodes": {
        "lhs-01": {"ActiveFeatures": "(null)", "AllocMem": "0", "AllocTRES": "", "Arch": "x86_64",
                   "AvailableFeatures": "(null)", "AveWatts": "0", "Boards": "1", "BootTime": "2022-03-03T08:34:24",
                   "CPUAlloc": "0", "CPULoad": "0.23", "CPUTot": "2", "CapWatts": "n/a", "CfgTRES": "cpu",
                   "CoresPerSocket": "1", "CurrentWatts": "0", "ExtSensorsJoules": "n/s", "ExtSensorsTemp": "n/s",
                   "ExtSensorsWatts": "0", "FreeMem": "2519", "Gres": "(null)", "MCS_label": "N/A",
                   "NodeAddr": "lhs-01", "NodeHostName": "lhs-01", "NodeName": "lhs-01", "Owner": "N/A",
                   "Partitions": "debug", "RealMemory": "1024", "SlurmdStartTime": "2022-03-03T08:34:32",
                   "Sockets": "2", "State": "IDLE", "ThreadsPerCore": "1", "TmpDisk": "0", "Version": "19.05.5",
                   "Weight": "1"},
        "lhs-02": {"ActiveFeatures": "(null)", "AllocMem": "0", "AllocTRES": "", "Arch": "x86_64",
                   "AvailableFeatures": "(null)", "AveWatts": "0", "Boards": "1", "BootTime": "2022-03-03T08:42:45",
                   "CPUAlloc": "0", "CPULoad": "0.18", "CPUTot": "2", "CapWatts": "n/a", "CfgTRES": "cpu",
                   "CoresPerSocket": "1", "CurrentWatts": "0", "ExtSensorsJoules": "n/s", "ExtSensorsTemp": "n/s",
                   "ExtSensorsWatts": "0", "FreeMem": "3075", "Gres": "(null)", "MCS_label": "N/A",
                   "NodeAddr": "lhs-02", "NodeHostName": "lhs-02", "NodeName": "lhs-02", "Owner": "N/A",
                   "Partitions": "debug", "RealMemory": "1024", "Reason": "Node",
                   "SlurmdStartTime": "2022-03-03T08:42:52", "Sockets": "2", "State": "DOWN", "ThreadsPerCore": "1",
                   "TmpDisk": "0", "Version": "19.05.5", "Weight": "1"}}}
    for k in data:
        redis_cli.set(k, json.dumps(data[k]), ex=3600 * 72)
        # print(redis_cli.get(k))


get_slurm_jobs()
# test_redis()
