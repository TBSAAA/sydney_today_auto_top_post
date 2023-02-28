import os
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

import requests
import local_settings
import Connect



def get_access_token():
    url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?"
    params = {
        "corpid": local_settings.Wechat['corpid'],
        "corpsecret": local_settings.Wechat['corpsecret'],
    }
    res = requests.get(url, params=params)
    access_token = res.json()['access_token']
    print("get access_token")
    return access_token


def send_message(loop_num, info_level, content):
    if loop_num == 0:
        return
    if info_level == 1:
        touser = local_settings.Wechat['touser-1']
    elif info_level == 2:
        touser = local_settings.Wechat['touser-2']
    with Connect.Connect() as conn:
        sql = "SELECT access_token FROM wechat_token where id=1"
        access_token = conn.fetch_one(sql)['access_token']
    url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + access_token
    data = {
        "touser": touser,
        "msgtype": "text",
        "agentid": 1000002,
        "text": {
            "content": content
        },
    }
    res = requests.post(url, json=data)
    if res.json()['errcode'] != 0:
        print('access_token expired')
        access_token = get_access_token()
        with Connect.Connect() as conn:
            sql = "UPDATE wechat_token SET access_token='{}' where id=1".format(access_token)
            conn.execute(sql)
        send_message(loop_num - 1, info_level, content)


if __name__ == '__main__':
    send_message(3, 2, "小福福来了")
