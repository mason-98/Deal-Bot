import asyncio
import discord
import redditScrapper
from discord.ext import commands
from discord.utils import get
import User
import database


def get_deals(amount, url, deal_name):
    list_of_deals = redditScrapper.populate_by_num(int(amount), url, deal_name)
    return list_of_deals


def check_value(value1, value2):
    if (value1 == value2) & (value1 != 'Unavailable'):
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
            if check_value(last_deal.fields[0].value, deals[i].fields[0].value) | \
                    check_value(last_deal.fields[1].value, deals[i].fields[1].value) | \
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
        self.channel = {'bapcsale': 'BAPCSaleCanada Deal', 'videogamedeals': 'Video Game Deal'}
        self.url = {'bapcsale': 'https://old.reddit.com/r/bapcsalescanada/new/',
                    'videogamedeals': 'https://old.reddit.com/r/VideoGameDealsCanada/new/'}
        self.last_deal = {}
        self.index = 0
        self.members = database.db_get_all_users()

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is ready')
        channels = database.db_get_channels()
        for channel in channels:
            self.channel[channel[0]] = channel[1]
            self.url[channel[0]] = channel[2]
            channel1 = get(self.bot.guilds[0].channels, name=channel[0], type=discord.ChannelType.text)
            self.bot.loop.create_task(new_post(channel1, self, channel[2], channel[0]))

    @commands.command()
    async def ping(self, ctx):
        """
        Test server latency
        Parameters
        ----------
        ctx : the context of the command
        """
        await ctx.send(f'Pong! {round(self.bot.latency * 1000)}ms')

    @commands.command()
    async def add(self, ctx, *, message):
        """
        Add term to watchlist
        Parameters
        ----------
        ctx : the context of the command
        message: the message sent by the user
        """
        user = User.User(ctx.author.name, ctx.author.discriminator)

        if self.members:
            if (ctx.author.name, ctx.author.discriminator) in self.members:
                self.members[(ctx.author.name, ctx.author.discriminator)].add_item(message, ctx.channel.name)
                user = self.members[(ctx.author.name, ctx.author.discriminator)]
            else:
                user.add_item(message, ctx.channel.name)
                self.members[(ctx.author.name, ctx.author.discriminator)] = user
        else:
            user.add_item(message, ctx.channel.name)
            self.members[(ctx.author.name, ctx.author.discriminator)] = user
        database.db_insert_user(user)
        await ctx.send(message + " Add to wishlist")

    @commands.command()
    async def remove(self, ctx, *, message):
        """
        Add term to watchlist
        Parameters
        ----------
        ctx : the context of the command
        message: the message sent by the user
        """
        user = User.User(ctx.author.name, int(ctx.author.discriminator))
        for index in range(0, len(self.members), 1):
            if user.check_user(self.members[index]):
                self.members[index].add_item(message, ctx.channel.name)
                user = self.members[index]
            elif index == len(self.members)-1:
                user.add_item(message, ctx.channel.name)
                self.members.append(user)
        database.db_insert_user(user)
        await ctx.send(message + " Add to wishlist")

    @commands.command()
    async def wishlist(self, ctx):
        embed = discord.Embed(title=ctx.author.display_name + " " + self.channel[ctx.channel.name] + " Wishlist",
                              colour=0xe67e22)
        user = User.User(ctx.author.name, ctx.author.discriminator)
        if (ctx.author.name, ctx.author.discriminator) in self.members:
            member = self.members[(ctx.author.name, ctx.author.discriminator)]
            if ctx.channel.name in member.watchlists:
                for index in range(0, len(member.watchlists[ctx.channel.name]), 1):
                    embed.add_field(name='Wishlist Item #' + str(index+1),
                                    value=member.watchlists[ctx.channel.name][index], inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def clear(self, ctx, amount):
        await ctx.channel.purge(limit=int(amount) + 1)

    @commands.command()
    async def get(self, ctx, amount):
        key = ctx.channel.name
        list_of_deals = get_deals(amount, self.url[key], self.channel[key])
        for i in range(len(list_of_deals) - 1, -1, -1):
            await ctx.send(embed=list_of_deals[i])
        await self.set_last_deal(list_of_deals[0], key)
        return list_of_deals

    async def get_last_deal(self):
        return self.last_deal

    async def set_last_deal(self, last_deal, deal_name):
        self.last_deal[deal_name] = last_deal

    @commands.command()
    async def add_channel(self, ctx, channel_name):
        try:
            self.channel[ctx.channel.name] = channel_name
        except():
            await ctx.send("Invalid Channel Id Given")


async def new_post(channel, dealbot, url, channel_name):
    while True:
        deals = get_deals(5, url, dealbot.channel[channel_name])
        last_deal = dealbot.last_deal
        if last_deal:
            if channel_name in last_deal:
                new_deals, check = check_post(deals, dealbot.last_deal[channel_name])
            else:
                new_deals, check = check_post(deals, None)
        else:
            new_deals, check = check_post(deals, None)
        if new_deals:
            if check:
                await dealbot.set_last_deal(new_deals[0], channel_name)
            for i in range(len(new_deals) - 1, -1, -1):
                users = []
                found_users = check_wishlists(new_deals[i], dealbot, channel_name)
                if len(found_users) != 0:
                    mentions = ''
                    for user in found_users:
                        dc_user = discord.utils.get(dealbot.bot.users, name=user[0], discriminator=user[1])
                        if dc_user:
                            mentions += dc_user.mention + ' '
                    new_deals[i].add_field(name='Users who should check out the deal', value=mentions)
                await channel.send(embed=new_deals[i])
        await asyncio.sleep(600)


def check_wishlists(deal, deal_bot, channel_name):
    ping_users = []
    if deal_bot.members:
        for key in deal_bot.members:
            if deal_bot.members[key].watchlists:
                if channel_name in deal_bot.members[key].watchlists:
                    if any(ele.lower() in deal.fields[-2].value.lower() for ele in
                           deal_bot.members[key].watchlists[channel_name]):
                        ping_users.append(key)
    return ping_users


bot = commands.Bot(command_prefix='.')
dealBot = DealBot(bot)
bot.add_cog(dealBot)
bot.run('NjU3MjY1MzUzMTQ3Mjg1NTI3.XfuvVw.jUe2OsoG5jCTlrzIodbVRATrur0')
