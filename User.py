class User:
    def __init__(self, name, num):
        self.name = name
        self.num = num
        self.watchlists = {'bapcsale': []}

    def get_watchlist(self, channel_name):
        if channel_name in self.watchlists:
            return self.watchlist[channel_name]

    def add_item(self, item, channel_name):
        if channel_name in self.watchlists:
            self.watchlists[channel_name].append(item)
        else:
            self.watchlists[channel_name] = [item]

    def remove_item(self, index, channel_name):
        if channel_name in self.watchlists:
            item = self.watchlists[channel_name].pop(index)
            return item
        return None

    def check_user(self, user):
        if (self.name == user.name) & (self.num == user.num):
            return True
        return False
