from nonebot import on_request, RequestSession
from nonebot import on_notice, NoticeSession
import sqlite3
import aiohttp

sqlconn = sqlite3.connect('C:\CQ\酷Q Pro\MltdBot.db')

@on_request('friend')
async def _(session: RequestSession):
    if session.ctx['comment'] == '765':
        await  session.approve()
        return
    await session.reject('验证错误')


@on_notice('group_increase')
async def _(session: NoticeSession):
    if session.ctx['user_id'] == session.ctx['self_id']:
        global sqlconn
        sqlconn.cursor().execute('INSERT INTO GroupInfo (GroupCode, IfPush) VALUES (?, ?)', (session.ctx['group_id'], True))
        sqlconn.commit()
        async with aiohttp.request('GET', 'https://api.matsurihi.me/mltd/v1/events') as resp:
            json = await resp.json()


@on_notice('group_decrease')
async def _(session: NoticeSession):
    if session.ctx['user_id'] == session.ctx['self_id']:
        global sqlconn
        sqlconn.cursor().execute('DELETE FROM GroupInfo WHERE GroupCode = ?', (session.ctx['group_id'],))
        sqlconn.commit()

