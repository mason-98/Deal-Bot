import os
import sqlite3
import User

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'user.sqlite3')


def db_connect(db_path=DEFAULT_PATH):
    conn = sqlite3.connect(db_path)
    return conn


def db_init():
    conn = db_connect()
    cur = conn.cursor()
    users_table = """
    CREATE TABLE IF NOT EXISTS users (
        name text NOT NULL,
        user_id text NOT NULL,
    primary key (name, user_id))
    """
    channel_table = """
    create table IF NOT EXISTS channels
    (
        channel_name text not null,
        deal_name text not null,
        scrape_url text,
    PRIMARY KEY (channel_name)
    );"""
    watchlist_table = """create table IF NOT EXISTS watchlists
    (
        channel_name text not null,
        user_name text not null,
        user_id text not null,
        watchlist text,
        primary key (user_name, user_id, channel_name));
    """
    cur.execute(channel_table)
    cur.execute(users_table)
    cur.execute(watchlist_table)
    conn.close()


def db_insert_user(user):
    conn = db_connect()
    cur = conn.cursor()
    if user.watchlists == {}:
        insert_sql = "INSERT OR IGNORE INTO users(name, user_id) VALUES (?, ?)"
        cur.execute(insert_sql, (user.name, user.num))
    else:
        insert_sql = "INSERT OR IGNORE INTO users(name, user_id) VALUES (?, ?)"
        cur.execute(insert_sql, (user.name, user.num))
        for key in user.watchlists:
            insert_sql = "INSERT OR REPLACE INTO watchlists(channel_name, user_name, user_id, watchlist) VALUES (?, " \
                         "?, ?, ?) "
            watchlist = '"{}"'.format('", "'.join(map(str, user.watchlists[key])))
            cur.execute(insert_sql, (key, user.name, user.num, watchlist))
    conn.commit()
    conn.close()


def db_insert_channel(chanel_name, deal_name, scrape_url):
    conn = db_connect()
    cur = conn.cursor()
    insert_sql = "INSERT INTO channels(channel_name, deal_name, scrape_url) VALUES (?, ?, ?)"
    cur.execute(insert_sql, (chanel_name, deal_name, scrape_url))
    conn.commit()
    conn.close()


def db_get_user_watchlist(user, channel_name):
    conn = db_connect()
    cur = conn.cursor()
    watchlist_sql = "SELECT watchlist FROM watchlists where user_name=? and user_id=? and channel_name=?"
    cur.execute(watchlist_sql, (user.name, user.num, channel_name))
    results = cur.fetchall()
    conn.close()
    if results:
        return results[0][0]
    return None


def db_get_user_watchlists(user):
    conn = db_connect()
    cur = conn.cursor()
    watchlist_sql = "SELECT watchlist, channel_name FROM watchlists where user_name=? and user_id=?"
    cur.execute(watchlist_sql, (user.name, user.num))
    results = cur.fetchall()
    conn.close()
    if results:
        return results
    return None


def db_update_watchlist(user, channel_name):
    conn = db_connect()
    cur = conn.cursor()
    update_sql = "UPDATE watchlists SET watchlist = ? where user_name=? and user_id=? and channel_name=?"
    cur.execute(update_sql, (', '.join('"{0}"'.format(w) for w in user.watchlists), user.name, user.num, channel_name))
    conn.commit()
    conn.close()


def db_get_all_users():
    conn = db_connect()
    cur = conn.cursor()
    user_sql = "SELECT * FROM users"
    cur.execute(user_sql)
    results = cur.fetchall()
    conn.close()
    if results:
        users = {}
        for result in results:
            cur_user = User.User(result[0], result[1])
            user_watchlists = db_get_user_watchlists(cur_user)
            for watchlist in user_watchlists:
                for item in watchlist[0].split(','):
                    cur_user.add_item(eval(item), watchlist[1])
            users[(result[0], result[1])] = cur_user
        return users
    return {}


def db_drop_tables():
    conn = db_connect()
    cur = conn.cursor()
    delete_sql1 = "DROP TABLE IF EXISTS watchlists"
    delete_sql2 = "DROP TABLE IF EXISTS users"
    delete_sql3 = "DROP TABLE IF EXISTS channels"
    cur.execute(delete_sql1)
    cur.execute(delete_sql2)
    cur.execute(delete_sql3)
    conn.close()


def db_get_channels():
    conn = db_connect()
    cur = conn.cursor()
    channels_sql = "SELECT * FROM channels"
    cur.execute(channels_sql)
    results = cur.fetchall()
    conn.close()
    if results:
        channels = []
        for result in results:
            channels.append([result[0], result[1], result[2]])
        return channels
    return None


# user = User.User('test', 1)
# user.add_item("4k", "bapcsale")
# user.add_item("spiderman", "videogamedeals")
# user2 = User.User('admin', 2)
# user2.add_item("1440p", "bapcsale")
# db_insert_user(user2)
# db_insert_user(user)
# db_insert_channel('bapcsale', 'BAPCSaleCanada Deal', 'https://old.reddit.com/r/bapcsalescanada/new/')
# db_insert_channel('videogamedeals', 'Video Game Deal', 'https://old.reddit.com/r/VideoGameDealsCanada/new/')
# users = db_get_all_users()
# for user in users:
#     print(user.name)
#     print(user.num)
#     print(user.watchlists)