import os
import sys

import local_settings

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

import requests
import time
import random
from datetime import datetime
import Connect

token = ""
sbid = ""
uid = ""

headers = {
    "sbtype": "2",
    "vsion": "1",
    "version": "1480",
    "sbid": sbid,
    "token": token,
    "content-type": "application/x-www-form-urlencoded",
    "accept-encoding": "gzip",
    "user-agent": "okhttp/4.9.1",
}


def get_top_post():
    url = "https://app4.dayqly.com/life/user/myPosts"
    data = {
        "domain_id": "2113",
        "state_id": "2114",
        "uid": uid,
        "cateid": "2",
        "page": "1",
    }
    res = requests.post(url, data=data, headers=headers)
    print("get top post states: {}, msg: {}".format(res.json()['status'], res.json()['msg']))
    ads = res.json()['data']['rows']
    for ad in ads:
        with Connect.Connect() as conn:
            sql = "select table_sign from selection_type where id = '{}'".format(ad['classify'])
            type = conn.fetch_one(sql)['table_sign']

            if type == 'yellowpage':
                count = 1
            elif type == 'business':
                count = 4
            elif type == 'rent':
                count = 3
            elif type == 'market':
                count = 3
            else:
                count = 3
            sql = "insert into task_list values ('%s','%s','%s','%s','%s',%s)" % (
                ad['_id'], ad['title'], type, token, sbid, count)
            conn.execute(sql)


def keep_alive():
    url = "https://app4.dayqly.com/user/keep/"
    data = {
        "domain_id": "2113",
        "state_id": "2114",
        "lasttime": "0",
        "lastid": "0",
        "page": "1",
        "type": "news",
        "version": "1480",
        "sbid": sbid,
        "token": token,
    }
    res = requests.post(url, data=data, headers=headers)
    print("keep alive states: {}, msg: {}".format(res.json()['status'], res.json()['msg']))
    time.sleep(1)
    res.close()


def share_post():
    url = "https://app4.dayqly.com/share/topic/"
    data = {
        "sbid": sbid,
        "token": token,
    }
    res = requests.post(url, data=data, headers=headers)
    print("share post states: {}, msg: {}".format(res.json()['status'], res.json()['msg']))
    time.sleep(1)
    res.close()


def get_selection_type():
    url = "https://www.findonet.com/config/appInfo/sectionType.json"
    headers = {
        "sbtype": "2",
        "vsion": "1",
        "version": "1480",
        "sbid": "765a1b370d19492f7489df0db56b7114",
        "accept-encoding": "gzip",
        "user-agent": "okhttp/4.9.1",
    }
    res = requests.get(url, headers=headers)
    data_list = []
    for k, v in res.json().items():
        for detail in v:
            data_list.append((int(detail['id']), detail['type'], detail['table']))
    with Connect.Connect() as conn:
        sql = "delete from selection_type"
        conn.execute(sql)
        sql = "insert into selection_type(id,type,table_sign) values (%s,%s,%s)"
        conn.execute_many(sql, data_list)


if __name__ == '__main__':
    get_selection_type()
    with Connect.Connect() as conn:
        sql = "delete from task_list"
        conn.execute(sql)
        sql = "select * from acc_cookies"
        accounts = conn.fetch_all(sql)
        for account in accounts:
            token = account['token']
            sbid = account['sbid']
            uid = account['uid']
            print(token, sbid, uid)
            get_top_post()
            keep_alive()
            share_post()

    currentDateAndTime = datetime.now()
    currentDateAndTime = currentDateAndTime.strftime("%H:%M:%S %d/%m/%Y")
    print('preparations completed--------', currentDateAndTime)

    # Because of the top-post rule, the same type can only be top-posted once, and one must be deleted.
    with Connect.Connect() as conn:
        sql = "select ad_id from task_list WHERE token = '{}'".format(local_settings.sydney_today['token'])
        ad_ids = conn.fetch_all(sql)
        # get random int number, 0 or 1
        random_index = random.randint(0, 1)
        ad_id = ad_ids[random_index]['ad_id']
        sql = "delete from task_list where ad_id = '{}'".format(ad_id)
        conn.execute(sql)
