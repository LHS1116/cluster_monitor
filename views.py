# -*- coding: utf-8 -*-
""" 
@Describe: 
@Time    : 2022/2/19 5:48 下午
@Author  : liuhuangshan
@File    : views.py
"""
import os

from flask import Blueprint, render_template, abort, Response, Request, jsonify, request
from utils import *

job_view = Blueprint('job_view', __name__, url_prefix='/job')
node_view = Blueprint('node_view', __name__, url_prefix='/node')
user_view = Blueprint('user_view', __name__, url_prefix='/user')
resource_view = Blueprint('resource_view', __name__, url_prefix='/resource')
alert_view = Blueprint('alert_view', __name__, url_prefix='/alert')


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


@alert_view.route('/create', methods=['POST'])
def create_alert_info():
    """alert_manager发送告警信息"""
    register_dict = request.form
    print(register_dict)

    pass


@alert_view.route('/alerts')
def get_alerts():
    """获取历史告警记录"""
    pass


@alert_view.route('/alert/<string:user_name>')
def get_alerts_by_user(user_name: str):
    """获取用户历史告警记录"""
    pass
