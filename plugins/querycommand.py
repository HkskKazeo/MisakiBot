import nonebot
from nonebot import on_command, CommandSession
import sqlite3


#各一次性档线查询接口


@on_command('event', only_to_me=False, aliases=('档线', '活动档线', '档线查询', '当前档线', 'pt档线'))
async def event(session: CommandSession):
    sqlconn = sqlite3.connect('MltdBot.db')
    sqlcursor = sqlconn.cursor()
    result = sqlcursor.execute('SELECT * FROM GlobalVars where VarName = ? LIMIT 1', ('str_ptnew',))
    values = result.fetchall()
    if len(values) > 0:
        await session.send(str(values[0][1]))
    else:
        await session.send('未找到数据。')


@on_command('highscore', only_to_me=False, aliases=('高分档线', '高分', '高分查询', '活动曲档线', '活动曲排行'))
async def event(session: CommandSession):
    sqlconn = sqlite3.connect('MltdBot.db')
    sqlcursor = sqlconn.cursor()
    result = sqlcursor.execute('SELECT * FROM GlobalVars where VarName = ? LIMIT 1', ('str_hsnew',))
    values = result.fetchall()
    if len(values) > 0:
        await session.send(str(values[0][1]))
    else:
        await session.send('未找到数据。')


# 历史档线查询，根据关键字查找最多3个活动
@on_command('eventhis', only_to_me=False, aliases=('历史档线', '历史活动档线', '历史pt档线', '历史档线查询', '过去档线'))
async def eventhis(session: CommandSession):
    typename = {3: '传统', 4: '巡演'}
    word = session.get('str')
    sqlconn = sqlite3.connect('MltdBot.db')
    sqlcursor = sqlconn.cursor()
    result = sqlcursor.execute('SELECT ID, Name, Type, BeginTime, EndTime, BoostStart FROM EventInfo where ID = ? OR \
        Name like ? LIMIT 3', (word, '%'+word+'%'))
    values = result.fetchall()
    resultstr = ''
    for j in values:
        resultstr += '活动名称: ' + str(j[1]) + '\n类型: ' + typename[j[2]] + \
                    '\n开始时间: ' + str(j[3]) + '\n结束时间： ' + str(j[4]) +\
                     '\n折返时间: ' + str(j[5]) + '\n'
        resultstr = checkevent(sqlcursor, j[0], resultstr)
    await session.send(resultstr)


@eventhis.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if stripped_arg:
       session.state['str'] = stripped_arg
    else:
        session.finish('格式错误，请使用活动序号或活动的部分关键字来查询。\n例:【历史档线 100】或【历史活动档线 君花火】')


def checkevent(cursor, id, resultstr):
    result = cursor.execute("select Rank, EventPT, PTIncrease from Eventhistory where EventID = ? and Time = \
    (select max(time) from EventHistory where EventID = ?) ORDER BY Rank", (id, id, ))
    values = result.fetchall()
    for j in values:
        resultstr += str(j[0]) + ':\t' + str(j[1]) + '(+' + str(j[2]) + ')\n'
    resultstr += '\n'
    return resultstr


@on_command('highscorehis', only_to_me=False, aliases=('历史高分', '历史高分查询', '历史高分档线', '历史活动曲档线'))
async def highscorehis(session: CommandSession):
    typename = {3: '传统', 4: '巡演'}
    word = session.get('str')
    sqlconn = sqlite3.connect('MltdBot.db')
    sqlcursor = sqlconn.cursor()
    result = sqlcursor.execute('SELECT ID, Name, Type, BeginTime, EndTime, BoostStart FROM EventInfo where ID = ? OR \
        Name like ? LIMIT 3', (word, '%'+word+'%'))
    values = result.fetchall()
    resultstr = ''
    for j in values:
        resultstr += '活动名称: ' + str(j[1]) + '\n类型: ' + typename[j[2]] + \
                    '\n开始时间: ' + str(j[3]) + '\n结束时间： ' + str(j[4]) +\
                     '\n折返时间: ' + str(j[5]) + '\n'
        resultstr = checkevent(sqlcursor, j[0], resultstr)
    await session.send(resultstr)



@highscorehis.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if stripped_arg:
        session.state['str'] = stripped_arg
    else:
        session.finish('格式错误，请使用活动序号或活动的部分关键字来查询。\n例:【历史高分 100】或【历史高分档线 HARMONY】')


def checkevent(cursor, id, resultstr):
    result = cursor.execute("select Rank, EventPT, PTIncrease from EventHighscore where EventID = ? and Time = \
    (select max(time) from EventHighscore where EventID = ?) ORDER BY Rank", (id, id, ))
    values = result.fetchall()
    for j in values:
        resultstr += str(j[0]) + ':\t' + str(j[1]) + '(+' + str(j[2]) + ')\n'
    resultstr += '\n'
    return resultstr