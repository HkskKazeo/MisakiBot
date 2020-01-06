import nonebot
import sqlite3
import aiohttp
from . import predict
from datetime import datetime
import asyncio


# 档线更新;预测更新
@nonebot.scheduler.scheduled_job('cron', minute='18,48')
async def _():
    trycount = 0
    while trycount < 5:
        try:
            async with aiohttp.request('GET', 'https://api.matsurihi.me/mltd/v1/events') as resp:
                if resp.status == 200:
                    json = await resp.json()
                    break
                await asyncio.sleep(1)
        except:
            trycount += 1
            await asyncio.sleep(1)
            print('update_except', trycount)
            pass
    if trycount == 5:
        print('event_read_failed')
        return
    print("event_read_success")
    time = datetime.strptime(json[-1]['schedule']['endDate'], "%Y-%m-%dT%H:%M:%S+09:00")
    sqlconn = sqlite3.connect('Misaki.db')
    cursor = sqlconn.cursor()
    if json[-1]['type'] == 3 or json[-1]['type'] == 4:

        eventlength, boostlength = check_eventinfo(sqlconn, cursor, json[-1])

        # 更新pt档线
        strpredict = '预测结果：'
        for i in (1, 2, 3, 10, 100, 2500, 5000, 10000, 25000, 50000):
            trycount = 0
            while trycount < 5:
                try:
                    str_rank = 'https://api.matsurihi.me/mltd/v1/events/' + str(json[-1]['id']) \
                               + '/rankings/logs/eventPoint/' + str(i)
                    async with aiohttp.request('GET', str_rank) as resp:
                        if resp.status == 200:
                            json_rank = await resp.json()
                            break
                except:
                    trycount += 1
                    await asyncio.sleep(1)
                    print('update_except_rank', i, trycount)
                    pass
            if trycount == 5:
                print('rank_read_failed', i)
                continue
            print("rank_read_success", i)
            try:
                nowhours = dbwrite_event(sqlconn, json[-1]['id'], i, json_rank)
            except:
                print('数据为空')
                continue
            # 更新档线预测
            if 2500 <= i <= 50000:
                # 更新档线预测
                print(json_rank[0]['data'][-1]['summaryTime'])
                if nowhours > eventlength - boostlength and nowhours % 6 == 0:
                    strpredict += predict.event_predict(sqlconn, json[-1]['id'], json[-1]['type'], i, int(eventlength),
                                                        int(boostlength), int(nowhours), json_rank)
            # 更新档线对比
            if 2500 == i and nowhours > 0.5:
                generate_comparestr(sqlconn, cursor, json[-1]['name'], json[-1]['type'], eventlength, nowhours, json_rank)

        # 写入档线更新结果
        timelast = datetime.strptime(json_rank[0]["data"][-1]["summaryTime"], "%Y-%m-%dT%H:%M:%S+09:00")
        result = cursor.execute("SELECT * FROM EventHistory where EventID = ? AND Time = ? ORDER BY Rank",
                                (json[-1]['id'], timelast))
        values = result.fetchall()
        generate_ptstr(sqlconn, cursor, values, json[-1]['name'])

        # 预测结果更新
        if nowhours > eventlength - boostlength and nowhours % 6 == 0:
            strpredict = '活动名称：' + json[-1]['name'] + '\n预测时间：' + json_rank[0]["data"][-1]["summaryTime"] + '\n'\
                         + strpredict
            cursor.execute('Update GlobalVars SET Value = ? where VarName = ?', (strpredict, 'str_predict'))
            cursor.execute('Insert Into PredictHistory(Time, text) VALUES (?, ?)',
                           (timelast, strpredict))
            sqlconn.commit()

        # 检查预警并更新
        bot = nonebot.get_bot()
        msgtype, user, msg = check_alarms(sqlconn, values)
        try:
            for i in range(len(msgtype)):
                if i == 1:
                    print(user[i], msg[i])
                    await bot.send_private_msg(user_id=user[i], message=msg[i])
                else:
                    print(user[i], msg[i])
                    await bot.send_group_msg(group_id=user[i], message=msg[i])
        except:
            pass

        # 更新高分档线
        for i in (1, 2, 3, 10, 100, 2000, 5000, 10000, 20000):
            trycount = 0
            while trycount < 5:
                try:
                    str_hs = 'https://api.matsurihi.me/mltd/v1/events/' + str(json[-1]['id']) \
                               + '/rankings/logs/highScore/' + str(i)
                    async with aiohttp.request('GET', str_hs) as resp:
                        if resp.status == 200:
                            json_hs = await resp.json()
                            break
                except:
                    trycount += 1
                    await asyncio.sleep(1)
                    print('update_except_hs', i, trycount)
                    pass
            if trycount == 5:
                print('hs_read_failed', i)
                continue
            print("hs_read_success", i)
            dbwrite_hs(sqlconn, json[-1]['id'], i, json_hs)

        timelast = datetime.strptime(json_rank[0]["data"][-1]["summaryTime"], "%Y-%m-%dT%H:%M:%S+09:00")
        result = cursor.execute("SELECT * FROM EventHighScore where EventID = ? AND Time = ? ORDER BY Rank",
                                (json[-1]['id'], timelast))
        values = result.fetchall()
        generate_hsstr(sqlconn, cursor, values, json[-1]['name'])


    else:
        reset_str(sqlconn, cursor)


# 写入本次活动基本信息
def check_eventinfo(sqlconn, sqlcursor, json):
        time_s = datetime.strptime(json["schedule"]["beginDate"], "%Y-%m-%dT%H:%M:%S+09:00")
        time_e = datetime.strptime(json["schedule"]["endDate"], "%Y-%m-%dT%H:%M:%S+09:00")
        time_b = datetime.strptime(json["schedule"]["boostBeginDate"], "%Y-%m-%dT%H:%M:%S+09:00")
        length = (time_e - time_s).days * 24.0 + ((time_e - time_s).seconds + 1) / 3600.0
        boostlength = (time_e - time_b).days * 24.0 + ((time_e - time_b).seconds + 1) / 3600.0
        sqlcursor.execute("INSERT INTO EventInfo (ID, Name, Type, BeginTime, EndTime, Length, BoostStart, \
            BoostLength) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (json["id"], json["name"],
                                                     json["type"], time_s, time_e, length, time_b,
                                                     boostlength))
        sqlconn.commit()
        return length, boostlength


# 倒序写入本次活动档线更新，直到遇到一条已存在的记录
def dbwrite_event(sqlconn, id, rank, json_rank):
    lasttime = datetime.strptime(json_rank[0]['data'][-1]["summaryTime"], "%Y-%m-%dT%H:%M:%S+09:00")
    timestart = datetime.strptime(json_rank[0]["data"][0]["summaryTime"],
                                  "%Y-%m-%dT%H:%M:%S+09:00")
    timestart = datetime(timestart.year, timestart.month, timestart.day, 15, 0, 0)
    hoursnow = (lasttime - timestart).days * 24.0 + (lasttime - timestart).seconds / 3600.0

    for j in reversed(json_rank[0]['data']):
        cursor = sqlconn.cursor()
        timestamp = datetime.strptime(j["summaryTime"], "%Y-%m-%dT%H:%M:%S+09:00")
        result = cursor.execute(
            "SELECT * FROM EventHistory where EventID = ? AND Rank = ? AND Time = ?", (id, rank, timestamp))
        if len(list(result)) == 0:
            hours = (timestamp - timestart).days * 24.0 + (timestamp - timestart).seconds / 3600.0
            if json_rank[0]["data"].__len__ == 1:
                diff = j["score"]
            else:
                diff = j["score"] - json_rank[0]["data"][json_rank[0]["data"].index(j) - 1]["score"]
            cursor.execute("INSERT INTO EventHistory (EventID, Rank, Time, HoursAfterBegin, \
            EventPT, PTIncrease) VALUES(?, ?, ?, ?, ?, ?)", (id, rank, timestamp, hours, j["score"], diff))
            sqlconn.commit()
        else:
            break
    return hoursnow


# 创建档线查询字符串
def generate_ptstr(sqlconn, sqlcursor, values, name):
    if len(values) > 0:
        str_ptnew = '活动名称: ' + name + '\n更新时间: ' + str(values[0][2]) + '(日本时间)' \
                    '\n已经过: ' + str(values[0][3]) + '小时\n=======================\n'+ '\t档线\t\t分数\n'
        for j in values:
            str_ptnew += '\t' + str(j[1]) + '\t \t' + str(j[4]) + '(+' + str(j[5]) + ')\n'
        sqlcursor.execute('Update GlobalVars SET Value = ? where VarName = ?', (str_ptnew, 'str_ptnew'))
        sqlconn.commit()

# 统计历史活动当前时点的档线，创建查询字符串
def generate_comparestr(sqlconn, cursor, name, type, eventlength, nowhours, json_rank):
    if len(json_rank[0]["data"]) < 2:
        return
    pt = str(json_rank[0]["data"][-1]["score"])
    inc = str(json_rank[0]["data"][-1]["score"] - json_rank[0]["data"][-2]["score"])
    str_ptcomp = '活动名称： ' + name + '\n当前经过时间：' + str(nowhours) + \
                 '\n当前一档pt及增速: ' + pt + '(' + inc + ')' +\
                 '\n历史活动数据(名称，现时点pt, 现时点增速，最终pt)\n'
    result = cursor.execute(
        "SELECT A.EventPT, A.PTIncrease, B.EventPT, C.Name FROM EventInfo C \
        INNER JOIN EventHistory A On A.EventID = C.ID AND A.Rank = 2500 AND A.HoursAfterBegin = ? \
        INNER JOIN EventHistory B On B.EventID = C.ID AND B.Rank = 2500 AND B.HoursAfterBegin > C.Length \
        WHERE C.Type = ? AND C.Length = ?", (nowhours, type, eventlength))
    values = result.fetchall()
    for j in values:
        str_ptcomp +=  str(j[3]) + '\n' + str(j[0]) + '\t' + str(j[1]) + '\t' + str(j[2]) + '\n'
    if len(values) > 0:
        cursor.execute('Update GlobalVars SET Value = ? where VarName = ?', (str_ptcomp, 'str_ptcomp'))
    sqlconn.commit()


# 倒序写入本次活动高分更新，直到遇到一条已存在的记录
def dbwrite_hs(sqlconn, id, rank, json_rank):
    for j in reversed(json_rank[0]['data']):
        cursor = sqlconn.cursor()
        timestamp = datetime.strptime(j["summaryTime"], "%Y-%m-%dT%H:%M:%S+09:00")
        result = cursor.execute(
            "SELECT * FROM EventHighScore where EventID = ? AND Rank = ? AND Time = ?", (id, rank, timestamp))
        if len(list(result)) == 0:
            timestart = datetime.strptime(json_rank[0]["data"][0]["summaryTime"],
                                          "%Y-%m-%dT%H:%M:%S+09:00")
            timestart = datetime(timestart.year, timestart.month, timestart.day, 15, 0, 0)
            hours = (timestamp - timestart).days * 24.0 + (timestamp - timestart).seconds / 3600.0
            cursor.execute("INSERT INTO EventHighScore (EventID, Rank, Time, HoursAfterBegin, \
            HighScore) VALUES(?, ?, ?, ?, ?)", (id, rank, timestamp, hours, j["score"]))
            sqlconn.commit()
        else:
            break


# 创建高分查询字符串
def generate_hsstr(sqlconn, sqlcursor, values, name):
    if len(values) > 0:
        str_ptnew = '活动名称: ' + name + '\n更新时间: ' + str(values[0][2]) + ' (日本时间)'\
                    '\n已经过: ' + str(values[0][3]) + '小时\n=======================\n'+ '\t档线\t\t分数\n'
        for j in values:
            str_ptnew += '\t' + str(j[1]) + '\t \t' + str(j[4]) + '\n'
        sqlcursor.execute('Update GlobalVars SET Value = ? where VarName = ?', (str_ptnew, 'str_hsnew'))
        sqlconn.commit()


# 重置档线/高分查询字符串
def reset_str(sqlconn, sqlcursor):
    sqlcursor.execute('Update GlobalVars SET Value = ? where VarName = ? OR VarName = ? OR VarName = ?',
                      ('当前不在活动时段内，请使用历史档线查询功能。', 'str_ptnew', 'str_hsnew', 'str_ptcomp',))
    sqlcursor.execute('Update GlobalVars SET Value = ? where VarName = ?',
                      ('当前不在活动时段内或未到开始预测的时点(首次预测结果更新在后半段开始后6小时)。', 'str_predict'))
    sqlconn.commit()


# 检查是否存在被触发的档线报警,并触发通知
def check_alarms(sqlconn, values):
    cursor = sqlconn.cursor()
    result = cursor.execute("SELECT * FROM EventAlarmInfo order by Rank", ())
    alarmlist = result.fetchall()
    msgtype = []
    user = []
    msg = []
    for i in values:
        print(i[0], i[1], i[2], i[3], i[4])
    for j in alarmlist:
        print(j[0], j[1], j[2], j[3])
        for i in values:
            if j[2] == i[1]:
                if j[3] <= i[4]:
                    cursor.execute("DELETE FROM EventAlarmInfo Where UserID = ?", (j[1],))
                    strsend = "您设置的Rank " + str(i[1]) + " 档线预警已经触发！设置值为 " + str(j[3]) + \
                          ", 当前值为 " + str(i[4])
                    if j[0] == -1: #私聊发送提示
                        msgtype.append(1)
                        user.append(j[1])
                        msg.append(strsend)
                    else: #群内发送并@
                        strsend = '[CQ:at,qq=' + str(j[1]) + ']' + strsend
                        msgtype.append(0)
                        user.append(j[0])
                        msg.append(strsend)
                break

    sqlconn.commit()
    return msgtype, user, msg
