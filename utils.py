# -*- coding: utf-8 -*-
""" 
@Describe: 
@Time    : 2022/1/19 5:06 下午
@Author  : liuhuangshan
@File    : utils.py
"""
import json
import time
import requests
import redis
from typing import List, Dict, Union

from itsdangerous import TimedSerializer, TimestampSigner

from models import SlurmJob, SlurmNode, SlurmPartition

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

sec_key = "w183$sjOv&"
serializer = TimedSerializer(sec_key)
signer = TimestampSigner(sec_key)
redis_cli = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def dumps_data():
    """将data用sec_key 加密"""
    data = {'a': 111, 'b': [222, 333]}
    _data = serializer.dumps(data)
    return _data

# def loads_data


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

def get_slurm_diag():
    """生成诊断信息"""
    return ''


def get_slurm_nodes(node_id: int = None, node_name: str = None) -> List[SlurmNode]:

    pass


def get_slurm_jobs(job_id: int = None, job_name: str = None) -> List[SlurmJob]:
    pass


def get_slurm_partition() -> List[SlurmPartition]:
    pass
def do_upload_data(data: dict):
    assert isinstance(data, dict), 'wrong format!'
    for k in data:
        json_str = json.dumps(data[k])
        redis_cli.set(k, json_str, ex=600)
    for k in data:
        print(k, json.loads(redis_cli.get(k)))
        print('=' * 30)


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

