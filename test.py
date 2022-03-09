import datetime
import random

import requests


def test():
    minutes = 10
    uid = f'slurm_job{random.Random().randint(1, 100)}'
    print(uid)
    saved = 0
    while 1:
        try:
            url = f'http://192.168.137.12:8000/api/data/test?min={minutes}&uid={uid}&saved={saved}'
            r = requests.get(url)
            js = r.json()
            # print(js)
            assert isinstance(js, dict)
            saved = js['saved']
            if js.get('success') == 1:
                break
        except Exception as e:
            print(e)
            break
columns = ['User', 'JobID', 'Partition', 'JobName', 'State', 'AllocTRES', 'AllocGRES', 'AllocCPUS', 'QOS', 'AveCPU','ReqCPUS', 'CPUTime', 'TotalCPU', 'UserCPU', 'ReqTRES', 'Submit', 'Start', 'End']

