# -*- coding: utf-8 -*-
""" 
@Describe: 
@Time    : 2022/2/19 5:48 下午
@Author  : liuhuangshan
@File    : views.py
"""
import os
import sys
import traceback

from flask import Blueprint, render_template, abort, Response, Request, jsonify, request
from utils import *

job_view = Blueprint('job_view', __name__, url_prefix='/job')
node_view = Blueprint('node_view', __name__, url_prefix='/node')
user_view = Blueprint('user_view', __name__, url_prefix='/user')
resource_view = Blueprint('resource_view', __name__, url_prefix='/resource')
alert_view = Blueprint('alert_view', __name__, url_prefix='/alert')
data_view = Blueprint('data_view', __name__, url_prefix='/data')


@job_view.route('/jobs')
def get_jobs():
    """获取当前作业列表"""
    pass


@job_view.route('/job/<int:job_id>')
def get_job_by_id(job_id):
    """根据id获取作业"""
    pass


@job_view.route('/job/<string:user_name>')
def get_job_by_user(user_name: str):
    """获取用户运行中作业"""
    pass


@job_view.route('/job/history/<string:user_name>')
def get_history_job_by_user(user_name: str):
    """获取用户历史作业"""
    pass


@user_view.route('/user/users')
def get_users():
    """获取当前用户列表"""
    pass


@user_view.route('/user/<int:user_id>')
def get_user_by_id(user_id):
    """根据id获取用户"""
    pass


@node_view.route('/nodes')
def get_nodes():
    """获取节点信息"""
    nodes = get_slurm_nodes()
    return nodes, 200


@resource_view.route('/total')
def get_cluster_resource_info():
    """获取集群资源信息"""
    pass


@resource_view.route('/job/<int:job_id>')
def get_job_resource_info(job_id: int):
    """获取作业资源使用信息"""
    pass


@resource_view.route('/user/<string:user_name>')
def get_user_resource_info(user_name: str):
    """获取用户资源使用信息"""
    pass


@resource_view.route('/node/<string:node_name>')
def get_node_resource_info(node_name: str):
    """获取节点资源使用信息"""
    pass


@alert_view.route('/create', methods=['POST', 'GET'])
def create_alert_info():
    """alert_manager发送告警信息"""

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

    try:
        register_dict = request.form or request.json
        # TODO: 做出操作
        # request.headers
        print(register_dict)

        return jsonify(register_dict)
    except Exception as e:
        print(e)
        traceback.print_tb(sys.exc_info()[2])
        return str(e)
    pass


@alert_view.route('/alerts')
def get_alerts():
    """获取历史告警记录"""
    pass


@alert_view.route('/alert/<string:user_name>')
def get_alerts_by_user(user_name: str):
    """获取用户历史告警记录"""
    pass


@data_view.route('/upload', methods=['POST'])
def upload_data():
    try:
        token = request.headers.get('Token')
        if verify_token(token):
            data = request.form or request.json
            do_upload_data(data)
            return 'success', 200
        else:
            return 'invalid token!', 403
    except Exception as e:
        print(e)
        traceback.print_tb(sys.exc_info()[2])
        return str(e), 200
