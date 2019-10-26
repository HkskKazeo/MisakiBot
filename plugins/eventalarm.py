from nonebot import on_command, CommandSession
import sqlite3


# 档线预警添加与删除
@on_command('eventalarm', only_to_me=False, aliases=('档线预警', '档线报警', '档线提示'))
async def eventalarm(session: CommandSession):
    sqlconn = sqlite3.connect('Misaki.db')
    sqlcursor = sqlconn.cursor()
    result = sqlcursor.execute('SELECT * FROM EventAlarmInfo where UserID = ?', (int(session.ctx['user_id']),))
    values = result.fetchall()
    if len(values) > 0:
        await session.send('你已设置了其他报警， 设置值为Rank' + str(values[0][2]) + '达到' + str(values[0][3])
                           + '时进行报警。现删除。')
        delete_alarm(sqlconn, int(session.ctx['user_id']))
    if session.state['type'] == 2:  # 群内发送
        sqlcursor.execute('Insert Into EventAlarmInfo values(?, ?, ?, ?)', (int(session.ctx['group_id']),
                          int(session.ctx['user_id']), session.state['rank'], session.state['value']))
    else:   # 私聊发送
        sqlcursor.execute('Insert Into EventAlarmInfo values(?, ?, ?, ?)', (-1,
                          int(session.ctx['user_id']), session.state['rank'], session.state['value']))
    sqlconn.commit()
    await session.send('设置成功！')


@eventalarm.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.split(' ')
    if session.ctx['message_type'] == 'group':
        session.state['type'] = 2
    else:
        session.state['type'] = 1
    if stripped_arg:
        session.state['rank'] = int(stripped_arg[0])
        session.state['value'] = int(stripped_arg[1])
        if session.state['rank'] not in (1,2,3,10,100,2500,5000,10000,25000,50000):
            session.finish('rank错误,可用的rank包括1, 2, 3, 10, 100, 2500, 5000, 10000, 25000, 50000')
    else:
        session.finish('格式错误，请使用档线报警 Rank 设定值的格式设定。\n例: \
                       【档线报警 2500 300000】表示在Rank2500的档线达到300000以上时进行通知')


@on_command('eventalarmcancel', only_to_me=False, aliases=('取消预警', '取消报警', '预警取消', '报警取消'))
async def eventalarmcancel(session: CommandSession):
    sqlconn = sqlite3.connect('Misaki.db')
    delete_alarm(sqlconn, int(session.ctx['user_id']))
    sqlconn.commit()
    await session.send('取消成功！')


def delete_alarm(sqlconn, userid):
    sqlcursor = sqlconn.cursor()
    sqlcursor.execute('Delete from EventAlarmInfo where UserID = ?', (userid, ))
    sqlconn.commit()

