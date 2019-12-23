class User:
    def __init__(self, name, num):
        self.name = name
        self.num = num
        self.watchlist = []

    def get_watchlist(self):
        return self.watchlist

    def add_item(self, item):
        self.watchlist.append(item)

    def remove_item(self, index):
        item = self.watchlist.pop(index)
        return item
