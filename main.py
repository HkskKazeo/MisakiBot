from os import  path
import nonebot
import config  #设置
import asyncio


async def send_msg():
    print (nonebot.get_bot().asgi)
    await nonebot.get_bot().send_private_msg(user_id=594246389, message='closed')

if __name__ == '__main__':
    nonebot.init(config)
    nonebot.load_builtin_plugins()
    nonebot.load_plugins(
        path.join(path.dirname(__file__), 'plugins'),
        'plugins'
    )
    nonebot.run()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_msg())

