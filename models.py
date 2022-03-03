# -*- coding: utf-8 -*-
""" 
@Describe: 
@Time    : 2022/1/20 5:21 下午
@Author  : liuhuangshan
@File    : models.py
"""
from flask import Response, jsonify
from datetime import datetime


class SlurmResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (list, dict)):
            response = jsonify(response)
        return super(Response, cls).force_type(response, environ)


class SlurmEntity:
    @classmethod
    def from_dict(cls, values: dict):
        if values is None or len(values) == 0:
            return None
        entity = cls()
        entity.__dict__.update(values)
        return entity

    def __str__(self):
        return str(self.__dict__)


class SlurmNode(SlurmEntity):
    name: str
    group_id: int
    state: str
    partition_name: str
    cpu_tot: int
    mem: int
    alloc_tres: str

    def __init__(self, name, group_id, state, partition_name, cpu_tot=None, mem=None, alloc_tres=None):
        self.name = name
        self.group_id = group_id
        self.state = state
        self.partition_name = partition_name
        self.cpu_tot = cpu_tot
        self.mem = mem
        self.alloc_tre = alloc_tres


class SlurmJob(SlurmEntity):
    job_id: int
    user: str
    node_name: str
    tres: dict
    submit_time: datetime
    start_time: datetime
    end_time: datetime
    qos: str


class SlurmPartition(SlurmEntity):
    name: str
    qos: str
    nodes: list
    state: str
    tres: dict


