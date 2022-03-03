# -*- coding: utf-8 -*-
""" 
@Describe: 
@Time    : 2022/2/23 5:44 下午
@Author  : liuhuangshan
@File    : test.py
"""
import subprocess

diag = """
*******************************************************
sdiag output at Wed Feb 23 01:39:54 2022 (1645609194)
Data since      Wed Feb 23 01:23:40 2022 (1645608220)
*******************************************************
Server thread count:  3
Agent queue size:     0
Agent count:          0
DBD Agent queue size: 32733

Jobs submitted: 8
Jobs started:   8
Jobs completed: 7
Jobs canceled:  0
Jobs failed:    0

Job states ts:  Wed Feb 23 01:39:40 2022 (1645609180)
Jobs pending:   0
Jobs running:   0

Main schedule statistics (microseconds):
	Last cycle:   8
	Max cycle:    2314
	Total cycles: 26
	Mean cycle:   162
	Mean depth cycle:  0
	Cycles per minute: 1
	Last queue length: 0

Backfilling stats
	Total backfilled jobs (since last slurm start): 0
	Total backfilled jobs (since last stats cycle start): 0
	Total backfilled heterogeneous job components: 0
	Total cycles: 0
	Last cycle when: Wed Dec 31 16:00:00 1969 (0)
	Last cycle: 0
	Max cycle:  0
	Last depth cycle: 0
	Last depth cycle (try sched): 0
	Last queue length: 0

Latency for 1000 calls to gettimeofday(): 19 microseconds

Remote Procedure Call statistics by message type
	REQUEST_PARTITION_INFO                  ( 2009) count:11     ave_time:307    total_time:3377
	MESSAGE_EPILOG_COMPLETE                 ( 6012) count:8      ave_time:363    total_time:2910
	REQUEST_RESOURCE_ALLOCATION             ( 4001) count:6      ave_time:1674307 total_time:10045843
	REQUEST_NODE_INFO                       ( 2007) count:6      ave_time:379    total_time:2275
	REQUEST_JOB_STEP_CREATE                 ( 5001) count:5      ave_time:5151   total_time:25755
	REQUEST_COMPLETE_JOB_ALLOCATION         ( 5017) count:5      ave_time:2964   total_time:14824
	REQUEST_STEP_COMPLETE                   ( 5016) count:5      ave_time:2443   total_time:12217
	REQUEST_JOB_READY                       ( 4019) count:5      ave_time:378    total_time:1891
	REQUEST_JOB_INFO                        ( 2003) count:5      ave_time:451    total_time:2256
	MESSAGE_NODE_REGISTRATION_STATUS        ( 1002) count:2      ave_time:395    total_time:790
	REQUEST_SUBMIT_BATCH_JOB                ( 4003) count:2      ave_time:5008815 total_time:10017630
	REQUEST_COMPLETE_BATCH_SCRIPT           ( 5018) count:2      ave_time:2408   total_time:4816
	REQUEST_STATS_INFO                      ( 2035) count:0      ave_time:0      total_time:0

Remote Procedure Call statistics by user
	root            (       0) count:62     ave_time:324751 total_time:20134584

Pending RPC statistics
	No pending RPCs

"""


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


def get_slurm_nodes():
    command = 'sinfo'
    a = subprocess.getoutput(command)
    print(a)
    a = format_data(a)
    print(a)
    return []

get_slurm_nodes()
