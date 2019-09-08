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
            sqlconn = sqlite3.connect('C:\CQ\酷Q Pro\MltdBot.db')
            cursor = sqlconn.cursor()
            for i in (1, 2, 3, 10, 100, 2500, 5000, 10000, 25000, 50000):
                str_rank = 'https://api.matsurihi.me/mltd/v1/events/' + str(json[-1]['id']) \
                           + '/rankings/logs/eventPoint/' + str(i)
                async with aiohttp.request('GET', str_rank) as resp_rank:
                    json_rank = await resp_rank.json()
                    for j in reversed(json_rank[0]['data']):
                        timestamp = datetime.strptime(j["summaryTime"], "%Y-%m-%dT%H:%M:%S+09:00")
                        result = cursor.execute("SELECT * FROM EventHistory where EventID = ? AND Rank = ? AND Time = ?",
                                               (json[-1]['id'], i, timestamp))
                        if len(list(result)) == 0:
                            timestart = datetime.strptime(json_rank[0]["data"][0]["summaryTime"],
                                                                   "%Y-%m-%dT%H:%M:%S+09:00")
                            timestart = datetime(timestart.year, timestart.month, timestart.day, 15, 0, 0)
                            hours = (timestamp - timestart).days * 24.0 + (timestamp - timestart).seconds / 3600.0
                            if json_rank[0]["data"].__len__ == 1:
                                diff = j["score"]
                            else:
                                diff = j["score"] - json_rank[0]["data"][json_rank[0]["data"].index(j)-1]["score"]
                            cursor.execute("INSERT INTO EventHistory (EventID, Rank, Time, HoursAfterBegin, \
                            EventPT, PTIncrease) VALUES(?, ?, ?, ?, ?, ?)", (json[-1]['id'], i, timestamp,
                                                                             hours, j["score"], diff))
                            sqlconn.commit()
                        else:
                            break
            timelast = datetime.strptime(json_rank[0]["data"][-1]["summaryTime"], "%Y-%m-%dT%H:%M:%S+09:00")
            result = cursor.execute("SELECT * FROM EventHistory where EventID = ? AND Time = ? ORDER BY Rank",
                           (json[-1]['id'], timelast))
            values = result.fetchall()
            if len(values) > 0:
                global str_ptnew
                str_ptnew = '活动名称: ' + json[-1]['name'] + '\n当前时间: ' + str(values[0][2]) +\
                      '\n已经过: ' + str(values[0][3]) + '小时\n========\n'
                for j in values:
                    str_ptnew += str(j[1]) + ':\t' + str(j[4]) + '(+' + str(j[5]) + ')\n'
                bot = nonebot.get_bot()
                await bot.send_private_msg(user_id=594246389, message=str_ptnew)


