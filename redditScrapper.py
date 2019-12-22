import datetime
import requests
import re
import discord
from bs4 import BeautifulSoup

curr_date = datetime.date.today().strftime('%Y-%m-%d')


class Deal:
    def __init__(self, post_URL='Unavailable', deal_link='Unavailable', status='Available', desc='Unavailable',
                 deal_price='Unavailable', date=curr_date):
        self.attr = {'Post URL': post_URL, 'Deal Link': deal_link, 'Deal Price': deal_price, 'Status': status,
                     'Description': desc, 'Date Posted': date}

    def to_string(self):
        embed = discord.Embed(title='BAPCSaleCanada Deal', colour=0xe67e22)
        for key in self.attr:
            embed.add_field(name=key, value=self.attr[key], inline=False)
        return embed


class BAPCDeals(Deal):
    def __init__(self, post_URL='Unavailable', deal_link='Unavailable', status='Available', desc='Unavailable',
                 deal_price='Unavailable', init_price='Unavailable', base_URL='https://old.reddit.com',
                 date=curr_date):
        self.attr = {'Post URL': base_URL + post_URL, 'Deal Link': deal_link, 'Deal Price': deal_price,
                     'Original Price': init_price, 'Status': status, 'Description': desc, 'Date Posted': date}


def populate_by_num(count, URL):
    headers = {'User-Agent': "Mozilla/5.0"}
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    list_of_posts = soup.select_one('div[id="siteTable"]')
    posts = list_of_posts.select('div[class*="thing id-t3"]')
    index = 0
    list_of_deals = []
    while count > 0 and index < len(posts):
        deal = parse_post(posts[index])
        list_of_deals.append(deal.to_string())
        index += 1
        count -= 1
    if count > 0:
        nxt_page = soup.select_one('span[class="next-button"] > a').attrs['href']
        list_of_deals.extend(populate_by_num(count, nxt_page))

    return list_of_deals


def parse_post(post):
    title_info = post.select_one('p[class="title"]')
    desc = title_info.text
    date_str = post.select_one('time').attrs['datetime']
    match = re.search(r'([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))', date_str)
    if match is not None:
        date = match.group()
    else:
        date = curr_date
    prices_str = []
    prices = []
    init_price = 'Unavailable'
    deal_price = 'Unavailable'
    for m in re.findall(r'\$([1-9][0-9]{0,2}(\,[0-9]{3})*(\.[0-9]{2})?)', desc):
        prices_str.append(m[0])
        prices.append(float(m[0].replace(',', '')))
    if len(prices) == 0:
        for m in re.findall(r'([1-9][0-9]{0,2}(\,[0-9]{3})*(\.[0-9]{2})?)', desc):
            prices_str.append(m[0])
            prices.append(float(m[0].replace(',', '')))
    if len(prices) == 1:
        deal_price = prices_str[0]
    elif len(prices) == 2:
        deal_price = prices_str[prices.index(min(prices))]
        init_price = prices_str[prices.index(max(prices))]
    elif len(prices) > 2:
        deal_price = prices_str[len(prices) - 1]
        init_price = prices_str[prices.index(max(prices))]
    post_URL = post.attrs['data-permalink']
    deal_link = post.attrs['data-url']
    if deal_link == post_URL:
        deal_link = 'Unavailable'

    deal = BAPCDeals(post_URL=post_URL, deal_link=deal_link, status='Available',
                     desc=title_info.text, deal_price=deal_price, init_price=init_price, date=date)
    return deal


class WebScraper:
    def __init__(self, URL):
        self.URL = URL

    def populate_by_num(self, count):
        pass

    def populate_till_last(self, _list):
        pass
