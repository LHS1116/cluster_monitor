# -*- coding: utf-8 -*-
""" 
@Describe: 
@Time    : 2022/2/27 11:02 上午
@Author  : liuhuangshan
@File    : urls.py
"""
from flask import jsonify

from app import app
from views import *
app.register_blueprint(job_view)
app.register_blueprint(node_view)
app.register_blueprint(user_view)
app.register_blueprint(resource_view)
app.register_blueprint(alert_view)
app.register_blueprint(data_view)

@app.route('/hello')
def hello_world():
    return 'hello'
