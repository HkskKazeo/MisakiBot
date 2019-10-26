from nonebot import on_command, CommandSession
import numpy
import sqlite3
import os


# 控分计算命令
@on_command('theatersc', only_to_me=True, aliases=('传统控分', '上半月活动控分'))
async def theatersc(session: CommandSession):
    paras = session.get('para')
    str = theater_sc(int(paras[0]), int(paras[1]), int(paras[2]))
    await session.send(str);


@theatersc.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if stripped_arg:
        list = stripped_arg.split(' ')
        if len(list) == 3:
            session.state['para'] = list
        else:
            session.finish('格式错误，请在命令中包含 当前pt，当前道具，目标pt。\n例:【传统控分 0 0 765】')
    else:
        session.finish('格式错误，请在命令中包含 当前pt，当前道具，目标pt。\n例:【传统控分 0 0 765】')


@on_command('toursc', only_to_me=True, aliases=('巡演控分', '下半月活动控分'))
async def toursc(session: CommandSession):
    paras = session.get('para')
    str = tour_sc(int(paras[0]), int(paras[1]), int(paras[2]), int(paras[3]))
    await session.send(str);


@toursc.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if stripped_arg:
        list = stripped_arg.split(' ')
        if len(list) == 4:
            session.state['para'] = list
        else:
            session.finish('格式错误，请在命令中包含 当前pt，当前道具，当前道具进度(0-19), 目标pt。\n例:【传统控分 0 0 765】')
    else:
        session.finish('格式错误，请在命令中包含 当前pt，当前道具，当前道具进度(0-19), 目标pt。\n例:【传统控分 0 0 765】')


# 传统控分
def theater_sc(nowpt, nowitem, targetpt):

    count_30 = 0
    count_ev = 0
    if nowpt < 0 or nowpt > targetpt or nowitem < 0 or nowitem > 1000000 or targetpt < 0 or targetpt > 10000000:
        return '输入参数非法，无法求得结果！'
    while targetpt - nowpt > 2000:
        while nowitem < 180:
            nowitem += 85
            nowpt += 85
            count_30 += 1
        nowpt += 537
        nowitem -= 180
        count_ev += 1
    sqlconn = sqlite3.connect(os.path.abspath(os.path.dirname(os.getcwd())) + '/' + 'Misaki.db')
    sqlcursor = sqlconn.cursor()
    result = sqlcursor.execute("SELECT * FROM dp_theater where target = ?", (int(targetpt - nowpt),))
    values = result.fetchall()
    if len(values) == 0:
        return '无法求得结果，可能是目标pt与当前pt差值过小！'
    else:
        return '2M难度普通曲:\t' + str(values[0][2]) + '次\n' + '4M难度普通曲:\t' + str(values[0][3]) + '次\n' \
        + '6M难度普通曲:\t' + str(values[0][4]) + '次\n' + 'MM难度普通曲:\t' + str(values[0][5] + count_30) + '次\n' \
        + '活动曲:\t' + str(values[0][6] + count_ev) + '次\n*双倍按2次计算*'


# 巡演控分
# 默认5倍进度为0
def tour_sc(nowpt, nowitem, nowpos, targetpt):
    if nowpt < 0 or nowpt > targetpt or nowitem < 0 or nowitem > 99 or targetpt < 0 or targetpt > 10000000:
        return '输入参数非法，无法求得结果！'
    if nowitem > 20:
        return '道具过多(> 20)可能导致浪费，请清掉一部分再来!'
    count_30a = 0
    count_ev = 0
    nowitem *= 20
    nowitem += nowpos
    strres = ''
    while targetpt - nowpt > 4400: #这里写4400是因为4400以内的结果可以一次活动曲解决，不用再分配一次顺序
        count_30a += 8
        nowpt += 140 * 8
        nowitem += 48
        strres += 'MM1.2倍 8次\n'
        if nowitem > 60:
            count_ev += 3
            nowpt += 720 * 3
            nowitem -= 60
            strres += '5倍活动曲3次\n'
        else:
            count_ev += 2
            nowpt += 720 * 2
            nowitem -= 40
            strres += '5倍活动曲2次\n'
    sqlconn = sqlite3.connect(os.path.abspath(os.path.dirname(os.getcwd())) + '/' + 'Misaki.db')
    sqlcursor = sqlconn.cursor()
    result = sqlcursor.execute("SELECT * FROM dp_tour where target = ?", (int(targetpt - nowpt),))
    values = result.fetchall()
    if len(values) == 0:
        return '无法求得结果，可能是目标pt与当前pt差值过小！'
    else:
        (a15, b15, a20, b20, a25, b25, ev) = (values[0][2],values[0][3],values[0][4],values[0][5],values[0][6],values[0][7],values[0][8])
        a30 = 0
        b30 = 0
        if a15 >= 2:
            a30 = a15 // 2
            a15 = a15 % 2
        if b15 >= 2:
            b30 = b15 // 2
            b15 = b15 % 2
        if ev <= 3:
             if a15 > 0:
                 strres += '2M1.2倍 ' + str(a15) + '次\n'
             if b15 > 0:
                 strres += '2M1.0倍 ' + str(b15) + '次\n'
             if a20 > 0:
                 strres += '4M1.2倍 ' + str(a20) + '次\n'
             if b20 > 0:
                 strres += '4M1.0倍 ' + str(b20) + '次\n'
             if a25 > 0:
                 strres += '6M1.2倍 ' + str(a25) + '次\n'
             if b25 > 0:
                 strres += '6M1.0倍 ' + str(b25) + '次\n'
             if a30 > 0:
                 strres += 'MM1.2倍 ' + str(a30) + '次\n'
             if b30 > 0:
                 strres += 'MM1.0倍 ' + str(b30) + '次\n'
             if ev > 0:
                 strres += '活动曲5倍 ' + str(ev) + '次\n'
        else:
            return '无法求得结果，可能是目标pt与当前pt差值过小！'
        if len(strres) > 1300:
            return '结果过长无法显示。\n文本可以显示的极限pt差(目标pt - 当前pt)在20w左右。'
        else:
            # return len(strres)
            return strres + '*双倍按2次计算*'


# 传统控分: 生成dp结果存数据库
# 15体 item35 pt35
# 20体 item49 pt49
# 25体 item64 pt64
# 30体 item85 pt85
# event曲 统一消耗item180 pt537
def theater_sqlupdate():
    size = 2000
    # dp
    dp = numpy.full((size, 1000, 6), -1)
    for i in range(6):
        dp[0][0][i] = 0
    item = [35, 49, 64, 85, -180]
    pt = [35, 49, 64, 85, 537]
    cost = [15, 20, 25, 30, 0]
    for i in range(5):
        for j in range(size):
            for k in range(1000):
                if dp[j][k][0] >= 0:
                    if j + pt[i] < size and 0 <= k + item[i] < 1000:
                        if dp[j + pt[i]][k + item[i]][0] == -1 or dp[j + pt[i]][k + item[i]][0] > dp[j][k][0] + cost[i]:
                            dp[j + pt[i]][k + item[i]][0] = dp[j][k][0] + cost[i]
                            for t in range(5):
                                dp[j + pt[i]][k + item[i]][t + 1] = dp[j][k][t + 1]
                            dp[j + pt[i]][k + item[i]][i + 1] += 1

    sqlconn = sqlite3.connect(os.path.abspath(os.path.dirname(os.getcwd())) + '/' + 'Misaki.db')
    cursor = sqlconn.cursor()
    for j in range(size):
        res = []
        min = 1000
        for k in range(1000):
            if 0 <= dp[j][k][0] < min:
                res = [k, dp[j][k]]
                min = dp[j][k][0]
        if res != []:
            cursor.execute('Insert Into dp_theater(target, cnt15, cnt20, cnt25, cnt30, cntev) VALUES \
                           (?,?,?,?,?,?)', (j, int(res[1][1]), int(res[1][2]), int(res[1][3]), int(res[1][4]), int(res[1][5]),))
            sqlconn.commit()


# 巡演控分: 生成dp结果存数据库
# 15体 1.2倍 70
# 15体 1.0倍 58
# 20体 1.2倍 93
# 20体 1.0倍 77
# 25体 1.2倍 116
# 25体 1.0倍 96
# 30体 1.2倍 140
# 30体 1.0倍 116
# event曲 5.0倍 720 不考虑5倍以下
# 30体所有收益为15体2倍 故计算时可以先不考虑 生成结果时再转化
# 由于巡演打歌的顺序影响5倍进度条，而dp是按体力从低到高的顺序打的，得到的不一定是最优解
def tour_sqlupdate():
    size = 5001
    maxcost = 300
    dp = numpy.full((size, maxcost, 9), -1)
    for i in range(9):
        # 0：cost 1~6： 普通曲次数 7： 活动曲次数 8：当前5倍进度
        dp[0][0][i] = 0
    item = [3,3,4,4,5,5]
    pt = [70, 58, 93, 77, 116, 96]
    cost = [15, 15, 20, 20, 25, 25]
    # 这个伪dp非常zz
    for i in range(6):
        if i == 1:
            x = 0
        for j in range(size):
            for k in range(maxcost):
                if dp[j][k][7] > 0:
                    x = 0
                if dp[j][k][0] >= 0:
                    if j + pt[i] < size and 0 <= k + item[i] < maxcost:
                        if dp[j + pt[i]][k + item[i]][0] == -1 or dp[j + pt[i]][k + item[i]][0] > dp[j][k][0] + cost[i]\
                                or dp[j + pt[i]][k + item[i]][0] == dp[j][k][0] + cost[i] and dp[j + pt[i]][k + item[i]][8] < dp[j][k][8] + item[i]:
                            if dp[j + pt[i]][k + item[i]][7] > 0:
                                x = 0
                            for t in range(9):
                                dp[j + pt[i]][k + item[i]][t] = dp[j][k][t]
                            dp[j + pt[i]][k + item[i]][0] += cost[i]
                            dp[j + pt[i]][k + item[i]][i + 1] += 1
                            dp[j + pt[i]][k + item[i]][8] += item[i]
                            if dp[j + pt[i]][k + item[i]][8] >= 40:
                                # 5倍活动曲*1
                                if j + pt[i] + 720 < size and k + item[i] - 20 >= 0 and (dp[j + pt[i] + 720][k + item[i] - 20][0] == -1 or \
                                        dp[j + pt[i] + 720][k + item[i] - 20][0] > dp[j + pt[i]][k + item[i]][0]):
                                    for u in range(9):
                                        dp[j + pt[i] + 720][k + item[i] - 20][u] = dp[j + pt[i]][k + item[i]][u]
                                    dp[j + pt[i] + 720][k + item[i] - 20][7] += 1
                                    dp[j + pt[i] + 720][k + item[i] - 20][8] = 0
                                # 5倍活动曲*2
                                if j + pt[i] + 1440 < size and k + item[i] - 40 >= 0 and (dp[j + pt[i] + 1440][k + item[i] - 40][0] == -1 or \
                                        dp[j + pt[i] + 1440][k + item[i] - 40][0] > dp[j + pt[i]][k + item[i]][0]):
                                    for u in range(9):
                                        dp[j + pt[i] + 1440][k + item[i] - 40][u] = dp[j + pt[i]][k + item[i]][u]
                                    dp[j + pt[i] + 1440][k + item[i] - 40][7] += 2
                                    dp[j + pt[i] + 1440][k + item[i] - 40][8] = 0
                                # 5倍活动曲*3
                                if j + pt[i] + 2160 < size and k + item[i] - 60 >= 0 and (dp[j + pt[i] + 2160][k + item[i] - 60][0] == -1 or \
                                        dp[j + pt[i] + 2160][k + item[i] - 60][0] > dp[j + pt[i]][k + item[i]][0]):
                                    for u in range(9):
                                        dp[j + pt[i] + 2160][k + item[i] - 60][u] = dp[j + pt[i]][k + item[i]][u]
                                    dp[j + pt[i] + 2160][k + item[i] - 60][7] += 3
                                    dp[j + pt[i] + 2160][k + item[i] - 60][8] = 0

    sqlconn = sqlite3.connect('C:\CQ\MisakiBot\Misaki.db')
    cursor = sqlconn.cursor()
    for j in range(size):
        res = []
        min = 5001
        for k in range(maxcost):
            if 0 < dp[j][k][0] < min:
                res = [k, dp[j][k]]
                min = dp[j][k][0]
        if res != []:
            print(j, res[0], res[1])
            cursor.execute('Insert Into dp_tour(target, cnt15a, cnt15b, cnt20a, cnt20b, cnt25a, cnt25b, cntev) VALUES \
                           (?,?,?,?,?,?,?,?)', (j, int(res[1][1]), int(res[1][2]), int(res[1][3]), int(res[1][4]),
                                                int(res[1][5]),int(res[1][6]),int(res[1][7]),))
            sqlconn.commit()


if __name__ == '__main__':
    print(tour_sc(0, 0, 0, 765))
    print(theater_sc(0, 0, 765))


