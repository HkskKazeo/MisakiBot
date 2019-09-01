from nonebot import on_request, RequestSession
from nonebot import on_notice, NoticeSession


@on_request('friend')
async def _(session: RequestSession):
    if session.ctx['comment'] == '765':
        await  session.approve()
        return
    await session.reject('验证错误')


@on_request('group')
async def _(session: RequestSession):
    if session.ctx['sub_type'] == 'invite':
        await session.reject('test')


@on_notice('group_increase')
async def _(session: NoticeSession):
    bot = session.bot
    await bot.send_group_msg(group_id = 601031845, message = 'success')
    if session.ctx['user_id'] == session.ctx['self_id']:
        await  bot.send_group_msg(group_id = 601031845, message = 'isme')
