
from nonebot import on_command, CommandSession

#各一次性查询接口


@on_command('event', aliases=('档线', '活动档线', '档线查询', '当前档线', 'pt档线'))
async def _(session: CommandSession):
    global str_ptnew
    await session.send(str_ptnew)


@on_command('highscore', aliases=('高分档线', '高分', '高分查询', '活动曲档线', '活动曲排行'))
async def _(session: CommandSession):
    global str_hsnew
    await session.send(str_ptnew)


@on_command('eventhis', aliases=('历史档线', '历史活动档线', '历史pt档线', '历史档线查询', '过去档线'))
async def _(session: CommandSession):
    global str_hsnew
    await session.send(str_ptnew)



@on_command('highscorehis', aliases=('历史高分', '历史高分查询', '历史高分档线', '历史活动曲档线'))
async def _(session: CommandSession):
    global str_hsnew
    await session.send(str_ptnew)

