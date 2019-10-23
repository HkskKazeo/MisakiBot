from datetime import datetime
import sqlite3
import aiohttp
import urllib
from urllib import request
import json
import os


# 首次启动前执行
def init_database():

    sqlconn = sqlite3.connect(os.path.abspath(os.path.dirname(os.getcwd())) + '/' + 'Misaki.db')
    sqlcursor = sqlconn.cursor()

    str_catalog = 'https://api.matsurihi.me/mltd/v1/events'  # 活动列表
    req = urllib.request.Request(str_catalog)
    try:
        response = request.urlopen(str_catalog)
    except:
        exit()
    html = response.read()
    json_catalog = json.loads(html)
    finished = False
    for i in reversed(json_catalog):
        if i['id'] > 32 and (i["type"] == 3 or i["type"] == 4):  # 扩线后的传统/巡演
            time_s = datetime.strptime(i["schedule"]["beginDate"], "%Y-%m-%dT%H:%M:%S+09:00")
            time_e = datetime.strptime(i["schedule"]["endDate"], "%Y-%m-%dT%H:%M:%S+09:00")
            time_b = datetime.strptime(i["schedule"]["boostBeginDate"], "%Y-%m-%dT%H:%M:%S+09:00")
            length = (time_e - time_s).days * 24.0 + ((time_e - time_s).seconds + 1) / 3600.0
            boostlength = (time_e - time_b).days * 24.0 + ((time_e - time_b).seconds + 1) / 3600.0
            result = sqlcursor.execute("SELECT * FROM EventInfo WHERE ID = ?", (i["id"],))
            if len(list(result)) == 0:
                sqlcursor.execute("INSERT INTO EventInfo (ID, Name, Type, BeginTime, EndTime, Length, BoostStart, \
                        BoostLength) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (i["id"], i["name"], i["type"], time_s, time_e,
                                                                       length, time_b, boostlength))
            else:
                finished = True

            sqlconn.commit()
            for j in (1, 2, 3, 10, 100, 2500, 5000, 10000, 25000, 50000):
               read_rankpage(sqlconn, sqlcursor, i["id"], j)
            for j in (1, 2, 3, 10, 100, 2000, 5000, 10000, 20000):
               read_hspage(sqlconn, sqlcursor, i["id"], j)

            if finished:
                break


def read_rankpage(sqlconn, sqlcursor, event, rank):
    str_page = 'https://api.matsurihi.me/mltd/v1/events/' + str(event) + '/rankings/logs/eventPoint/' + str(rank)
    req = urllib.request.Request(str_page)
    try:
        response = request.urlopen(str_page)
    except:
        print('error' + str(event) + '_' + str(rank))
        return
    html = response.read()
    json_rank = json.loads(html)
    try:
        timestart = datetime.strptime(json_rank[0]["data"][0]["summaryTime"], "%Y-%m-%dT%H:%M:%S+09:00")
    except:
        return
    # 第一条记录的时间并非开始时间
    timestart = datetime(timestart.year, timestart.month, timestart.day, 15, 0, 0)
    for i in range(len(json_rank[0]["data"])):
        timenow = datetime.strptime(json_rank[0]["data"][i]["summaryTime"], "%Y-%m-%dT%H:%M:%S+09:00")
        hours = (timenow - timestart).days * 24.0 + (timenow - timestart).seconds / 3600.0
        score = json_rank[0]["data"][i]["score"]
        if (i == 0):
            diff = score
        else:
            diff = score - json_rank[0]["data"][i - 1]["score"]
        sqlcursor.execute("INSERT INTO EventHistory (EventID, Rank, Time, HoursAfterBegin, EventPT, PTIncrease) \
                              VALUES(?, ?, ?, ?, ?, ?)", (event, rank, timenow, hours, score, diff))
    sqlconn.commit()


def read_hspage(sqlconn, sqlcursor, event, rank):
    str_page = 'https://api.matsurihi.me/mltd/v1/events/' + str(event) + '/rankings/logs/highScore/' + str(rank)
    req = urllib.request.Request(str_page)
    try:
        response = request.urlopen(str_page)
    except:
        print('error' + str(event) + '_' + str(rank))
        return
    html = response.read()
    json_rank = json.loads(html)
    try:
        timestart = datetime.strptime(json_rank[0]["data"][0]["summaryTime"], "%Y-%m-%dT%H:%M:%S+09:00")
    except:
        return;
    # 第一条记录的时间并非开始时间
    timestart = datetime(timestart.year, timestart.month, timestart.day, 15, 0, 0)
    for i in range(len(json_rank[0]["data"])):
        timenow = datetime.strptime(json_rank[0]["data"][i]["summaryTime"], "%Y-%m-%dT%H:%M:%S+09:00")
        hours = (timenow - timestart).days * 24.0 + (timenow - timestart).seconds / 3600.0
        score = json_rank[0]["data"][i]["score"]
        sqlcursor.execute("INSERT INTO EventHighScore (EventID, Rank, Time, HoursAfterBegin, HighScore) \
                              VALUES(?, ?, ?, ?, ?)", (event, rank, timenow, hours, score))
    sqlconn.commit()

if __name__ == '__main__':
    init_database()