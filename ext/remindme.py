import discord
from discord.ext import commands
import time
import sqlite3
import asyncio
from prettytable import PrettyTable
import datetime
from math import ceil


class RemindMe:
    def __init__(self, bot):
        self.bot = bot
        self.prefix = bot.config['prefix']
        self.units = {'minute': 60,
                      'hour': 60*60,
                      'day': 60*60*24,
                      'week': 60*60*24*7,
                      'month': 60*60*24*7*30}

        self.conn = sqlite3.connect(self.bot.workdir + '/databases/remindme.db')
        self.cursor = self.conn.cursor()
        self.saved_reminders = []
        self.read_reminders()

    def read_reminders(self):
        # read_untill = time.time() + (60*60*25)  # read reminders of next 25h
        # _code = 'SELECT * FROM reminders WHERE FINISHES<{};'.format(read_untill)
        _code = 'SELECT * FROM reminders;'
        self.cursor.execute(_code)
        _res = self.cursor.fetchall()
        reminders = []
        for res in _res:
            reminder = dict()
            reminder['USER'] = res[0]
            reminder['SERVER'] = res[1]
            reminder['CHANNEL'] = res[2]
            reminder['FINISHES'] = int(res[3])
            reminder['MESSAGE'] = res[4]
            reminders.append(reminder)
        self.saved_reminders = reminders

    def add_reminder(self, user, server, channel, finishes, text):
        try:
            _code = 'INSERT INTO reminders VALUES ("{}", "{}", "{}", {}, "{}")'.format(user, server, channel, finishes, text)
            self.cursor.execute(_code)
            self.conn.commit()
            # if finishes < (time.time() + 60*60*25):  # only read reminders, if added one finishes in next 25h
            self.read_reminders()
            return True
        except Exception:
            return False

    def remove_all_reminders(self, user):
        _code = 'DELETE FROM reminders WHERE USER="{}";'.format(user)
        self.cursor.execute(_code)
        self.conn.commit()
        self.read_reminders()

    def remove_reminder(self, user, finishes, text):
        _code = 'DELETE FROM reminders WHERE USER="{}" AND FINISHES={} AND MESSAGE="{}";'.format(user, finishes, text)
        self.cursor.execute(_code)
        self.conn.commit()
        self.read_reminders()

    def get_reminders(self, user):
        return [(r['FINISHES'], r['MESSAGE']) for r in self.saved_reminders if r['USER'] == user]

    @commands.command(pass_context=True, no_pm=True)
    async def remindme(self, ctx, quantity: int=0, time_unit: str=None, *, text: str=None):
        if time_unit:
            time_unit = time_unit.lower()
            if time_unit.endswith("s"):
                time_unit = time_unit[:-1]
                s = 's'
            else:
                s = ''

        if (quantity > 0) and text and (time_unit in self.units):
            user = ctx.message.author.id
            server = ctx.message.server.id
            channel = ctx.message.channel.id
            seconds = quantity * self.units[time_unit]
            finishes = int(time.time() + seconds)
            self.add_reminder(user, server, channel, finishes, text)
            await self.bot.say('Will remind you in {} {}{}: "{}"'.format(str(quantity), time_unit, s, text))
        else:
            await self.bot.say('Usage: {}remindme <amount> <unit> <message>'.format(self.prefix))

    @commands.command(pass_context=True, no_pm=True)
    async def forgetme(self, ctx):
        user = ctx.message.author.id
        self.remove_all_reminders(user)
        await self.bot.say('\N{OK HAND SIGN}')

    @commands.command(pass_context=True, no_pm=True)
    async def reminders(self, ctx):
        user = ctx.message.author.id
        res = self.get_reminders(user)
        if not res:
            await self.bot.say('No reminders saved for you!')
            return

        t = PrettyTable()
        t.left_padding_width = 1
        t.right_padding_width = 1
        t.title = 'Your reminders'
        t.field_names = ['Time left', 'Msg']
        t.align['Time left'] = 'r'
        t.align['Msg'] = 'l'

        for r in res:
            time_str = '{:0>8}'.format(str(datetime.timedelta(seconds=r[0] - int(time.time()))))
            text_rows = ceil(len(r[1]) / 80)
            print(text_rows)
            row = [time_str, r[1][:80]]
            t.add_row(row)
            for i in range(1, text_rows):
                row = ['', r[1][80*i:80*(i+1)]]
                t.add_row(row)


        await self.bot.say('```{}```'.format(t.get_string()))

    async def check_reminders(self):
        while self is self.bot.get_cog('RemindMe'):
            for reminder in self.saved_reminders:
                if reminder['FINISHES'] <= int(time.time()):
                    all_servers = self.bot.servers
                    server = discord.utils.get(all_servers, id=str(reminder['SERVER']))
                    channel = server.get_channel(str(reminder['CHANNEL']))
                    user = discord.User(id=reminder['USER'])
                    await self.bot.send_message(channel, '{} Here is your reminder: "{}"'.format(user.mention, reminder["MESSAGE"]))
                    self.remove_reminder(reminder['USER'], reminder['FINISHES'], reminder['MESSAGE'])
            await asyncio.sleep(10)


def setup(bot):
    r = RemindMe(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(r.check_reminders())
    bot.add_cog(r)


if __name__ == '__main__':
    bot = commands.Bot('?')
    r = RemindMe(bot)
    r.get_reminders(104901117158121472)
