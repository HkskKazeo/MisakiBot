import nonebot
from nonebot import on_command, CommandSession
import sqlite3


#各一次性查询接口


@on_command('event', only_to_me=False, aliases=('档线', '活动档线', '档线查询', '当前档线', 'pt档线'))
async def _(session: CommandSession):
    sqlconn = sqlite3.connect('MltdBot.db')
    sqlcursor = sqlconn.cursor()
    result = sqlcursor.execute('SELECT * FROM GlobalVars where VarName = ? LIMIT 1', ('str_ptnew',))
    values = result.fetchall()
    if len(values) > 0:
        await session.send(str(values[0][1]))
    else:
        await session.send('未找到数据。')


@on_command('highscore', only_to_me=False, aliases=('高分档线', '高分', '高分查询', '活动曲档线', '活动曲排行'))
async def _(session: CommandSession):
    sqlconn = sqlite3.connect('MltdBot.db')
    sqlcursor = sqlconn.cursor()
    result = sqlcursor.execute('SELECT * FROM GlobalVars where VarName = ? LIMIT 1', ('str_hsnew',))
    values = result.fetchall()
    if len(values) > 0:
        await session.send(str(values[0][1]))
    else:
        await session.send('未找到数据。')


#历史档线查询，根据关键字查找最多3个活动
@on_command('eventhis', only_to_me=False, aliases=('历史档线', '历史活动档线', '历史pt档线', '历史档线查询', '过去档线'))
async def _(session: CommandSession):
    sqlconn = sqlite3.connect('MltdBot.db')
    sqlcursor = sqlconn.cursor()
    result = sqlcursor.exexute('SELECT ID FROM EventInfo where ID = ? OR Name like LIMIT 1', ())
    await session.send('result3')


@on_command('highscorehis', only_to_me=False, aliases=('历史高分', '历史高分查询', '历史高分档线', '历史活动曲档线'))
async def _(session: CommandSession):
    #global str_hsnew
    await session.send('result4')

