import os
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

import requests
import time
import Connect
from send_wechat import send_message

token = ""
sbid = ""


def top_post(task):
    headers = {
        "sbtype": "2",
        "vsion": "1",
        "version": "1480",
        "sbid": task['sbid'],
        "token": task['token'],
        "content-type": "application/x-www-form-urlencoded",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/4.9.1",
    }
    url = "https://app4.dayqly.com/user/topposts/"
    data = {
        "id": task['ad_id'],
        "type": task['type'],
        "sbid": task['sbid'],
        "token": task['token'],
    }
    count = task['count']
    res = requests.post(url, headers=headers, data=data)
    print("title= {}, states: {}, msg: {}".format(task['title'], res.json()['status'], res.json()['msg']))
    if res.json()['status'] == 200:
        count -= 1
        with Connect.Connect() as conn:
            if count == 0:
                sql = "delete from task_list where ad_id = '{}'".format(task['ad_id'])
                conn.execute(sql)
                msg = "{}--已经完成了今日的置顶任务".format(task['title'])
                send_message(3, 2, msg)
            else:
                sql = "update task_list set count = {} where ad_id = '{}'".format(count, task['ad_id'])
                conn.execute(sql)
                msg = "{}--还剩{}次置顶任务".format(task['title'], count)
                send_message(3, 1, msg)
    time.sleep(1)
    res.close()


def run():
    with Connect.Connect() as conn:
        sql = "select * from task_list"
        task_list = conn.fetch_all(sql)
        if task_list:
            for task in task_list:
                top_post(task)
                time.sleep(3)
        else:
            print("任务完成啦，等待明天吧")


if __name__ == '__main__':
    run()
