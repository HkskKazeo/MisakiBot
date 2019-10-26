from nonebot import on_command, CommandSession
import asyncio


# 帮助及关于
@on_command('help', only_to_me=True, aliases=('帮助',))
async def help(session: CommandSession):
    strhelp = '''当前此Bot可以使用的功能（命令）包括:
【档线查询】：查询当前活动的最新档线
【高分查询】：查询当前活动的最新活动曲高分榜
【历史档线】：查询过去活动的最终档线，可使用活动名称的一段来模糊查询
【历史高分】：查询过去活动的活动曲高分榜,同历史档线
【档线预警】：为档线设定一个预警值，当前活动档线超过此值时会@提醒，摸鱼水群好帮手
【档线预测】：用极其不精确的方式进行的当前活动最终分数线预测，在进入后半后每6小时更新一次
【传统控分】：根据当前活动进行状态计算得到某个特殊pt值的方式。对应了二周年后各难度活动曲收益统一的版本
【巡演控分】：同上，供巡演活动使用。如果差值较大可能会刷屏，请注意
【帮助】：就是你现在在看的这个... 
【关于】：版本更新，作者等信息。'''
    await session.send(strhelp)
    await asyncio.sleep(1000)
    strmore='''【使用注意事项】
1. 添加好友请输入验证信息'765'。添加好友后可以邀请到其他群。
2. 部分命令是只有私聊或在群内@机器人才会触发的。
3. 目前还处在测试阶段，出现返回异常或没有响应都是很常见的，请谅解。'''
    await session.send(strmore)


@on_command('about', only_to_me=True, aliases=('关于',))
async def help(session: CommandSession):
    strhelp = '''Misaki Bot
当前版本：V0.9.0
这是公开测试的第一个版本。

Bug反馈请联系作者QQ: 594246389；
或者前往MLTD贴吧的发布帖。

初期Bug修得差不多的时候会开源。
========
Misaki means 'Mltd Interactive Score-count Assistant KIt'
'''
    await session.send(strhelp)
