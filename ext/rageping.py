from discord.ext import commands
import asyncio


class RagePing:
    def __init__(self, bot):
        self.bot = bot
        self.prefix = self.bot.config['prefix']

    @commands.command(pass_context=True)
    async def rageping(self, ctx):
        """Repeats a ping five times"""
        msg = ctx.message
        role_mentions = msg.role_mentions
        user_mentions = msg.mentions

        async def print_usage():
            await self.bot.say('Usage: "{}rageping @ROLE <amount>"; You can mention one role/user '
                               'or a list of roles/users'.format(self.prefix))

        try:
            m_arr = msg.content.split(' ')
            amount = int(m_arr[len(m_arr) - 1])
            if amount > 20:
                await self.bot.say('Calm down! 20 pings max')
                return
        except ValueError:
            if ctx.message.content.endswith('>'):
                amount = 5
            else:
                await print_usage()
                return

        if role_mentions or user_mentions:
            for role_mention in role_mentions:
                mention = role_mention.mention
                for i in range(amount):
                    await self.bot.say(mention)
                    await asyncio.sleep(1)

            for user_mention in user_mentions:
                mention = user_mention.mention
                for i in range(amount):
                    await self.bot.say(mention)
                    await asyncio.sleep(1)

        else:
            await print_usage()


def setup(bot):
    bot.add_cog(RagePing(bot))
