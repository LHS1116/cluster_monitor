# -*- coding: utf-8 -*-
""" 
@Describe: 
@Time    : 2022/2/19 5:48 下午
@Author  : liuhuangshan
@File    : views.py
"""
import os
import random
import sys
import traceback
from datetime import timedelta

from flask import Blueprint, render_template, abort, Response, Request, jsonify, request
from utils import *

job_view = Blueprint('job_view', __name__, url_prefix='/api/job')
node_view = Blueprint('node_view', __name__, url_prefix='/api/node')
user_view = Blueprint('user_view', __name__, url_prefix='/api/user')
resource_view = Blueprint('resource_view', __name__, url_prefix='/api/resource')
alert_view = Blueprint('alert_view', __name__, url_prefix='/api/alert')
data_view = Blueprint('data_view', __name__, url_prefix='/api/data')


@job_view.route('/jobs')
def get_jobs():
    """获取当前作业列表"""
    jobs = get_slurm_jobs(return_dict=True)
    state = request.args.get('state')
    if state:
        jobs = list(filter(lambda x: x['state'] == 'running', jobs))
    summary = {}
    state_dict = {}
    part_dict = {}
    user_dict = {}
    for job in jobs:
        state = job.get('state')
        part = job.get('partition')
        user = job.get('user')
        state_count = state_dict.get(state, 0) + 1
        state_dict[state] = state_count
        part_count = part_dict.get(part, 0) + 1
        part_dict[part] = part_count
        user_count = user_dict.get(user, 0) + 1
        user_dict[user] = user_count
    summary['states'] = state_dict
    summary['partitions'] = part_dict
    summary['users'] = user_dict
    res = {
        'detail': jobs,
        'summary': summary
    }
    return jsonify(get_response(res, 200))


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
    resources = {

        'detail': {
            'gpu': {
                'total': 100,
                'alloc': 58,
                'idle': 42
            },
            'user': {
                'online': 10
            },
            'job': {
                'total': 2008,
                'fail': 160,
                'running': 708,
                'complete': 890,
                'pending': 157,
                'requeue_hold': 72
            },
        },
        'gpu_total': 100,
        'cpu_total': 108,
        'user_online': 7,
        'partition_total': 3,
        'running_job': 108,
        'alert_count': 2
    }
    return jsonify(get_response(resources, 200))


@resource_view.route('/job')
def get_job_resource_info():
    """获取作业资源使用信息"""
    pass


@resource_view.route('/partition/partitions')
def get_partition_resource_info():
    partitions = get_slurm_partition()
    return jsonify(get_response(partitions, 200))


@resource_view.route('/partition/timeGroup')
def get_partition_resource_info_group_by_time():
    """获取24h队列资源使用信息"""
    partition_time_utilization = get_slurm_partition_utilization_by_time()
    # fake data
    now = datetime.datetime.now().replace(minute=0, second=0)
    timeline = []
    for i in range(24):
        _time = now - timedelta(hours=i)
        timeline.append(_time.strftime('%H:%M'))
    timeline.reverse()
    partition_time_utilization = {
        'timeline': timeline,
        'utilization': {
            'dell': {
                'cpu': [round(random.random() * 100, 2) for i in range(24)],
                'gpu': [round(random.random() * 100, 2) for i in range(24)]
            },
            'sugon': {
                'cpu': [round(random.random() * 100, 2) for i in range(24)],
                'gpu': [round(random.random() * 100, 2) for i in range(24)]
            },
            'cpu': {
                'cpu': [round(random.random() * 100, 2) for i in range(24)],
                'gpu': [round(random.random() * 100, 2) for i in range(24)]
            }
        }
    }
    return jsonify(get_response(partition_time_utilization, 200))




@resource_view.route('/user/timeGroup')
def get_user_resource_info_group_by_time():
    """获取24h用户资源使用信息"""
    user_time_utilization = get_slurm_user_utilization_by_time()
    # fake data
    now = datetime.datetime.now().replace(minute=0, second=0)
    timeline = []
    for i in range(24):
        _time = now - timedelta(hours=i)
        timeline.append(_time.strftime('%H:%M'))
    timeline.reverse()
    user_time_utilization = {
        'timeline': timeline,
        'utilization': {
            'root_1': {
                'cpu': [round(random.random() * 100, 2) for i in range(24)],
                'gpu': [round(random.random() * 100, 2) for i in range(24)]
            },
            'root_2': {
                'cpu': [round(random.random() * 100, 2) for i in range(24)],
                'gpu': [round(random.random() * 100, 2) for i in range(24)]
            },
            'root_3': {
                'cpu': [round(random.random() * 100, 2) for i in range(24)],
                'gpu': [round(random.random() * 100, 2) for i in range(24)]
            }
        }
    }
    return jsonify(get_response(user_time_utilization, 200))


@resource_view.route('/user')
def get_user_resource_info():
    """获取用户资源使用信息"""
    jobs = get_today_jobs()
    user_resources = get_user_resource()
    res = {}
    for job in jobs:
        user = job.user
        user_info = res.get(user, {})
        # 记录作业状态数量
        user_states = user_info.get('state', {})
        stat = job.state
        if stat != 'running':
            count = user_states.get(stat, 0) + 1
            user_states[stat] = count
        else:
            running_jobs = user_states.get(stat, [])
            running_jobs.append(job.job_id)
            user_states[stat] = running_jobs
        user_info['state'] = user_info
        res[user] = user_info

    for user in user_resources:
        user_resources_info = user_resources[user]
        user_info = res.get(user)
        if user_info:
            user_info['cpu_alloc'] = user_resources_info.get('cpu_alloc', 0)
            user_info['gpu_alloc'] = user_resources_info.get('gpu_alloc', 0)
            user_info['cpu_used'] = user_resources_info.get('cpu_used', 0)
            user_info['gpu_used'] = user_resources_info.get('gpu_used', 0)
            user_info['total_job'] = sum(map(lambda x: user_info['state'].get(x, 0), user_info['state']))

            user_info['running_job'] = user_info.get('state').get('running', [])
            user_info['failed_job'] = user_info.get('state').get('failed', 0)
            user_info['completed_job'] = user_info.get('state').get('completed', 0)
            user_info['pending_job'] = user_info.get('state').get('pending', 0)
        res[user] = user_info

    res = {
        'root_1': {
            'cpu_alloc': 12,
            'gpu_alloc': 0,
            'cpu_used': 7,
            'gpu_used': 0,
            'total_jobs': 108,
            'failed_jobs': 8,
            'completed_jobs': 90,
            'pending_jobs': 7,
            'canceled_jobs': 0,
            'running_jobs': [1, 2, 3],

        },
        'root_2': {
            'cpu_alloc': 8,
            'gpu_alloc': 10,
            'cpu_used': 8,
            'gpu_used': 2,
            'total_jobs': 73,
            'failed_jobs': 6,
            'completed_jobs': 50,
            'pending_jobs': 7,
            'canceled_jobs': 5,
            'running_jobs': [4, 5, 6, 7, 8],
        }
    }
    return jsonify(get_response(res, 200))






@resource_view.route('/node/<string:node_name>')
def get_node_resource_info(node_name: str):
    """获取节点资源使用信息"""
    pass


@alert_view.route('/create', methods=['POST', 'GET'])
def create_alert_info():
    """alert_manager发送告警信息"""
    try:
        data = request.form or request.json
        solve_alert(data)
        return 'success', 200
    except Exception as e:
        print(e)
        traceback.print_tb(sys.exc_info()[2])
        return str(e)
    pass


@alert_view.route('/check')
def check_cancel_job():
    """查询需要关闭的作业"""
    try:
        jobs = get_cancel_job()
        return jobs
    except Exception as e:
        print(e)
        traceback.print_tb(sys.exc_info()[2])
        return str(e)


@alert_view.route('/callback', methods=['POST'])
def update_canceled_job():
    """更新关闭的作业"""
    try:

        token = request.headers.get('Token')
        if verify_token(token):
            data = request.form or request.json
            jobs = data.get('job_id')
            assert jobs is not None and isinstance(jobs, list)

            do_update_canceled_job(jobs)
            return {'message': 'ok'}, 200
        else:
            return {'message': 'invalid token!'}, 403

    except Exception as e:
        print(e)
        traceback.print_tb(sys.exc_info()[2])
        return str(e)


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

@data_view.route('/test')
def test_data():
    mins = float(request.args.get('min', 1))
    uid = request.args.get('uid', 1)
    saved = int(request.args.get('saved', 0))
    ruid = redis_cli.get(uid)
    if ruid:
        return {'success': 0, 'saved': 1}
    if not ruid and not saved:
        redis_cli.set(uid, 'ok', ex=int(mins * 60))
        return {'success': 0, 'saved': 1}
    elif not ruid and saved:
        return {'success': 1, 'saved': 1}
    return {'success': 0, 'saved': 0}


