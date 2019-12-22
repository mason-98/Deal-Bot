import redditScrapper
from discord.ext import commands, tasks
import asyncio


def get_deals(amount):
    list_of_deals = redditScrapper.populate_by_num(int(amount), 'https://old.reddit.com/r/bapcsalescanada/new/')
    return list_of_deals


def check_value(value1, value2):
    if value1 == value2:
        return True
    return False


def check_post(deals, last_deal):
    """
    Given a list of deals and the lastest deal check if that deal is already in the list
    :param deals: list of deals
    :param last_deal: the current latest deal
    :return: The new posts, True if we need to update the lastest deal
    """
    i = 0
    if last_deal is not None:
        # loop through the list of deals
        for i in range(len(deals) - 1, -1, -1):
            # Check if there is a matching post
            if check_value(last_deal.fields[0].value, deals[i].fields[0].value) |\
                    check_value(last_deal.fields[1].value, deals[i].fields[1].value) |\
                    check_value(last_deal.fields[-2].value, deals[i].fields[-2].value):
                # If the newest deal in the list is the same as the lastest deal than do nothing
                if i == 0:
                    return [], False
                # If a matching post is found than update the list of new deals up to that post
                return deals[0:i], True
    # Non match found so the whole list is new
    return deals, True


class DealBot(commands.Cog):
    """
    Deal bot that keeps track of user watchlist
    """

    def __init__(self, _bot):
        self.bot = _bot
        self.channel = 657266172785328140
        self.last_deal = None
        self.index = 0
        self.members = self.bot.get_all_members()

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is ready')
        self.bot.loop.create_task(new_post(self.bot.get_channel(self.channel), self))

    @commands.command()
    async def ping(self, ctx):
        """
        Test server latency
        Parameters
        ----------
        ctx : the context of the command
        """
        await ctx.send(f'Pong! {round(self.bot.latency * 1000)}ms')

    @commands.command(aliases=['wishlist'])
    async def add(self, ctx, *, message):
        """
        Add term to watchlist
        Parameters
        ----------
        ctx : the context of the command
        """
        await ctx.send("From: " + ctx.author._user.display_name + ctx.author._user.discriminator + " Msg: " + message)

    @commands.command()
    async def clear(self, ctx, amount):
        await ctx.channel.purge(limit=amount)

    @commands.command()
    async def get(self, ctx, amount):
        list_of_deals = get_deals(amount)
        for i in range(len(list_of_deals) - 1, -1, -1):
            await ctx.send(embed=list_of_deals[i])
        self.last_deal = list_of_deals[0]
        return list_of_deals

    async def get_last_deal(self):
        return self.last_deal

    async def set_last_deal(self, last_deal):
        self.last_deal = last_deal


async def new_post(channel, dealbot):
    while True:
        deals = get_deals(5)
        new_deals, check = check_post(deals, dealbot.last_deal)
        if new_deals:
            if check:
                await dealbot.set_last_deal(new_deals[0])
            for i in range(len(new_deals) - 1, -1, -1):
                await channel.send(embed=new_deals[i])
        await asyncio.sleep(600)


bot = commands.Bot(command_prefix='.')
dealBot = DealBot(bot)
bot.add_cog(dealBot)
bot.run('NjU3MjY1MzUzMTQ3Mjg1NTI3.XfuvVw.jUe2OsoG5jCTlrzIodbVRATrur0')
