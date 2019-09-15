import nonebot
import sqlite3
import aiohttp
from datetime import datetime


# 档线更新;预测更新
@nonebot.scheduler.scheduled_job('cron', minute='15, 45')
async def _():
    async with aiohttp.request('GET', 'https://api.matsurihi.me/mltd/v1/events') as resp:
        json = await resp.json()
    time = datetime.strptime(json[-1]['schedule']['endDate'], "%Y-%m-%dT%H:%M:%S+09:00")
    if (json[-1]['type'] == 3 or json[-1]['type'] == 4) and time > datetime.now():
        sqlconn = sqlite3.connect('MltdBot.db')
        cursor = sqlconn.cursor()
        check_eventinfo(sqlconn, cursor, json[-1])
        for i in (1, 2, 3, 10, 100, 2500, 5000, 10000, 25000, 50000):
            str_rank = 'https://api.matsurihi.me/mltd/v1/events/' + str(json[-1]['id']) \
                       + '/rankings/logs/eventPoint/' + str(i)
            async with aiohttp.request('GET', str_rank) as resp_rank:
                json_rank = await resp_rank.json()
            dbwrite_event(sqlconn, json[-1]['id'], i, json_rank)

        timelast = datetime.strptime(json_rank[0]["data"][-1]["summaryTime"], "%Y-%m-%dT%H:%M:%S+09:00")

        result = cursor.execute("SELECT * FROM EventHistory where EventID = ? AND Time = ? ORDER BY Rank",
                                (json[-1]['id'], timelast))
        values = result.fetchall()
        generate_rsstr(values, json[-1]['name'])

    else:
        global str_ptnew, str_hsnew
        str_ptnew = '当前不在活动时段内，请使用历史档线查询功能。'
        str_hsnew = '当前不在活动时段内，请使用历史档线查询功能。'


def check_eventinfo(sqlconn, sqlcursor, json):
        time_s = datetime.strptime(json["schedule"]["beginDate"], "%Y-%m-%dT%H:%M:%S+09:00")
        time_e = datetime.strptime(json["schedule"]["endDate"], "%Y-%m-%dT%H:%M:%S+09:00")
        time_b = datetime.strptime(json["schedule"]["boostBeginDate"], "%Y-%m-%dT%H:%M:%S+09:00")
        length = (time_e - time_s).days * 24.0 + (time_e - time_s).seconds / 3600.0
        boostlength = (time_e - time_b).days * 24.0 + (time_e - time_b).seconds / 3600.0
        sqlcursor.execute("INSERT INTO EventInfo (ID, Name, Type, BeginTime, EndTime, Length, BoostStart, \
            BoostLength) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (json["id"], json["name"],
                                                     json["type"], time_s, time_e, length, time_b,
                                                     boostlength))
        sqlconn.commit()


def dbwrite_event(sqlconn, id, rank, json_rank):
    for j in reversed(json_rank[0]['data']):
        cursor = sqlconn.cursor()
        timestamp = datetime.strptime(j["summaryTime"], "%Y-%m-%dT%H:%M:%S+09:00")
        result = cursor.execute(
            "SELECT * FROM EventHistory where EventID = ? AND Rank = ? AND Time = ?", (id, rank, timestamp))
        if len(list(result)) == 0:
            timestart = datetime.strptime(json_rank[0]["data"][0]["summaryTime"],
                                          "%Y-%m-%dT%H:%M:%S+09:00")
            timestart = datetime(timestart.year, timestart.month, timestart.day, 15, 0, 0)
            hours = (timestamp - timestart).days * 24.0 + (timestamp - timestart).seconds / 3600.0
            if json_rank[0]["data"].__len__ == 1:
                diff = j["score"]
            else:
                diff = j["score"] - json_rank[0]["data"][json_rank[0]["data"].index(j) - 1]["score"]
            cursor.execute("INSERT INTO EventHistory (EventID, Rank, Time, HoursAfterBegin, \
            EventPT, PTIncrease) VALUES(?, ?, ?, ?, ?, ?)", (id, rank, timestamp,
                                                             hours, j["score"], diff))
            sqlconn.commit()
        else:
            break


def generate_rsstr(values, name):
    if len(values) > 0:
        global str_ptnew
        str_ptnew = '活动名称: ' + name + '\n当前时间: ' + str(values[0][2]) + \
                    '\n已经过: ' + str(values[0][3]) + '小时\n========\n'
        for j in values:
            str_ptnew += str(j[1]) + ':\t' + str(j[4]) + '(+' + str(j[5]) + ')\n'




