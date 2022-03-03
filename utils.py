# -*- coding: utf-8 -*-
""" 
@Describe: 
@Time    : 2022/1/19 5:06 下午
@Author  : liuhuangshan
@File    : utils.py
"""
from typing import List, Dict, Union

from models import SlurmJob, SlurmNode, SlurmPartition
import subprocess


# def exec

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


def get_slurm_diag():
    """生成诊断信息"""
    return ''


def get_slurm_nodes(node_id: int = None, node_name: str = None) -> List[SlurmNode]:

    pass


def get_slurm_jobs(job_id: int = None, job_name: str = None) -> List[SlurmJob]:
    pass


def get_slurm_partition() -> List[SlurmPartition]:
    pass


