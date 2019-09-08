import nonebot
from nonebot import on_command, CommandSession


@on_command('test')
async def _(session: CommandSession):
    bot = nonebot.get_bot()
    await bot.send_private_msg(user_id=594246389, message='test')





