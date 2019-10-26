import sqlite3
import urllib.request
import json
import matplotlib.pyplot as plot
import pandas as pd
import os
from sklearn.linear_model import LinearRegression


# 活动档线自动预测
# paras: 活动类型 待预测排名 活动总长度 boost长度 当前经过长度 当前活动目前为止的增长记录
def event_predict(sqlconn, id, type, rank, eventlength, boostlength, nowhours, json_rank):

    # 预测方式： 从Boost开始，每6h更新一次
    # Boost后18h内： 使用当前总分数与同类型同长度活动对比做线性回归
    # Boost后24h起~42h： 使用24h内分数与同长度活动对比做线性回归
    # Boost后48h起~活动结束前6h： 使用此前24h分数与24~48h分数与所有活动对比做线性回归
    # rank包含2500,5000,10000,25000,50000
    print(eventlength, boostlength, nowhours, len(json_rank[0]['data']))
    if nowhours < eventlength - boostlength + 24:
        return predicttype1(sqlconn, id, type, rank, eventlength, nowhours, json_rank)
    elif nowhours < eventlength - boostlength + 48:
        return predicttype2(sqlconn, id, rank, eventlength, nowhours, json_rank)
    else:
        return predicttype3(sqlconn, id, rank, eventlength, nowhours, json_rank)


def predicttype1(sqlconn, id, type, rank, eventlength, nowhours, json_rank):
    size = len(json_rank[0]['data'])
    cursor = sqlconn.cursor()
    result = cursor.execute("SELECT * FROM EventHistory where Rank = ? AND EventID IN (SELECT ID FROM EventInfo \
                            where Type = ? AND Length = ? AND ID != ?) AND (HoursAfterBegin = ? or HoursAfterBegin > ?) \
                            ORDER BY EventID, HoursAfterBegin", (rank, type, eventlength, id, nowhours, eventlength,))
    values = result.fetchall()
    if len(values) > 0 and len(values) % 2 == 0:
        dict = {'row1': [], 'result': []}
        for i in values:
            if values.index(i) % 2 == 0:
                dict['row1'].append(i[4])
            if values.index(i) % 2 == 1:
                dict['result'].append(i[4]-dict['row1'][-1])
        data = pd.DataFrame(dict)
        x = data['row1'].values.reshape(-1, 1)
        y = data['result'].values.reshape(-1, 1)
        reg = LinearRegression()
        reg.fit(x, y)
        answer = reg.intercept_ + (reg.coef_[0] + 1) * json_rank[0]['data'][size - 1]['score']
        return '\n' + str(rank) + ':\t' + str(int(answer))
    else:
        return ""


def predicttype2(sqlconn, id, rank, eventlength, nowhours, json_rank):
    size = len(json_rank[0]['data'])
    cursor = sqlconn.cursor()
    result = cursor.execute("SELECT * FROM EventHistory where Rank = ? AND EventID IN (SELECT ID FROM EventInfo \
                            where Length = ? AND ID != ?) AND (HoursAfterBegin = ? OR HoursAfterBegin = ? OR \
                            HoursAfterBegin > ?)", (rank, eventlength, id, nowhours - 24, nowhours, eventlength,))
    values = result.fetchall()
    if len(values) > 0 and len(values) % 3 == 0:
        dict = {'row1': [], 'row2': [], 'result': []}
        for i in values:
            if values.index(i) % 3 == 0:
                dict['row1'].append(i[4])
            if values.index(i) % 3 == 1:
                dict['row2'].append(i[4] - dict['row1'][-1])
            if values.index(i) % 3 == 2:
                dict['result'].append(i[4] - dict['row1'][-1] - dict['row2'][-1])
        data = pd.DataFrame(dict)
        x = data['row2'].values.reshape(-1, 1)
        y = data['result'].values.reshape(-1, 1)
        reg = LinearRegression()
        reg.fit(x, y)
        answer = reg.intercept_ + reg.coef_[0] * (json_rank[0]['data'][size - 1]['score'] -
                                                  json_rank[0]['data'][size - 49]['score']) \
                 + json_rank[0]['data'][size - 1]['score']
        return '\n' + str(rank) + ':\t' + str(int(answer))
    else:
        return ""


def predicttype3(sqlconn, id, rank, eventlength, nowhours, json_rank):
    last = eventlength - nowhours
    size = len(json_rank[0]['data'])
    cursor = sqlconn.cursor()
    result = cursor.execute("select EventID, HoursAfterBegin, EventPT, Type from Eventhistory A INNER JOIN EventInfo B ON\
            (A.EventID = B.ID AND A.Rank = ? AND A.EventID != ? AND (A.HoursAfterBegin > B.Length or \
            A.HoursAfterBegin = B.Length - ? or A.HoursAfterBegin = B.Length - ? or A.HoursAfterBegin = B.Length - ?))",
            (rank, id, last + 48, last + 24, last,))
    values = result.fetchall()
    if len(values) > 0 and len(values) % 4 == 0:
        dict = {'row1': [], 'row2': [], 'row3': [], 'result': []}
        for i in values:
            if values.index(i) % 4 == 0:
                dict['row1'].append(i[2])
            if values.index(i) % 4 == 1:
                dict['row2'].append(i[2] - dict['row1'][-1])
            if values.index(i) % 4 == 2:
                dict['row3'].append(i[2] - dict['row1'][-1] - dict['row2'][-1])
            if values.index(i) % 4 == 3:
                dict['result'].append(i[2] - dict['row1'][-1] - dict['row2'][-1] - dict['row3'][-1])
        data = pd.DataFrame(dict)
        xs = data.drop(['result', 'row1'], axis = 1)
        y = data['result']
        reg = LinearRegression()
        reg.fit(xs, y)
        answer = reg.intercept_ + reg.coef_[0] * (json_rank[0]['data'][size - 49]['score'] -
                                                  json_rank[0]['data'][size - 97]['score']) \
                 + reg.coef_[1] * (json_rank[0]['data'][size - 1]['score'] -
                                   json_rank[0]['data'][size - 49]['score']) \
                 + json_rank[0]['data'][size - 1]['score']
        return '\n' + str(rank) + ':\t' + str(int(answer))
    else:
        return ""


# for test
def drawplot(sqlconn):
    cursor = sqlconn.cursor()
    result = cursor.execute("select EventID, HoursAfterBegin, EventPT, Type from Eventhistory A INNER JOIN EventInfo B ON\
                            (A.EventID = B.ID AND (A.HoursAfterBegin > B.Length or A.HoursAfterBegin = B.Length - ? \
                            or A.HoursAfterBegin = B.Length - ? or A.HoursAfterBegin = B.Length - ?) \
                            AND A.Rank = 5000 AND B.type > ?)", (96,72,48, 3))
    values = result.fetchall()
    dict = {'X':[], 'X1':[], 'X2':[], 'Y':[]}
    for i in values:
        if values.index(i) % 4 == 0:
            dict['X'].append(i[2])
        elif values.index(i) % 4 == 1:
            dict['X1'].append(i[2] - dict['X'][-1])
        elif values.index(i) % 4 == 2:
            dict['X2'].append(i[2] - dict['X1'][-1] - dict['X'][-1])
        else:
            dict['Y'].append(i[2] - dict['X2'][-1] - dict['X1'][-1] - dict['X'][-1])
    data = pd.DataFrame(dict)
    plot.plot(dict['X2'], dict['Y'], "or")
    last = data['X1'].values.reshape(-1, 1)
    #plot.plot(dict['X2'], 2.5 * last, "og")
    #plot.plot(dict['X2'], dict['X'], "og")
    x = data['X2'].values.reshape(-1, 1)
    xs = data.drop(['Y', 'X'], axis=1)
    y = data['Y']
    reg = LinearRegression()
    reg.fit(xs, y)
    y2 = reg.coef_[0] * last + reg.coef_[1] * x + reg.intercept_
    plot.plot(x, y2, "ob")
    plot.show()


if __name__ == '__main__':
    sqlconn = sqlite3.connect(os.path.abspath(os.path.dirname(os.getcwd())) + '/' + 'Misaki.db')
    sqlcursor = sqlconn.cursor()
    # aiohttp.request('GET', 'https://api.matsurihi.me/mltd/v1/events/100/rankings/logs/eventPoint/2500') as resp:
    #     json = resp.json()
    for i in (128.5, 129.0, 129.5, 130.0):
        if i % 3 == 0:
            print(i)
    # event_predict(sqlconn, 4, 2500, 174, 78, 150, json)
    for j in (102.0, 108.0, 114.0, 120.0, 126.0, 132.0, 138.0, 144.0, 150.0, 156.0, 162.0, 168.0):
        strresult = "预测结果："
        for i in (2500, 5000, 10000, 25000, 50000):
            url = 'https://api.matsurihi.me/mltd/v1/events/106/rankings/logs/eventPoint/' + str(i)
            req = urllib.request.urlopen(url).read()
            json_ev = json.loads(req)
            strresult += event_predict(sqlconn, 106, 4, i,  int(174.0), int(78.0), int(153), json_ev)
        #drawplot(sqlconn)
        print(strresult)
