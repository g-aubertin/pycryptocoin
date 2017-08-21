#!/usr/bin/env python

import bittrex, json

print bittrex.API_KEY
print bittrex.API_SECRET

coinlist = []

class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

class coin:
        """a coin:

    Attributes:
        name: coin name.
        balance: current balance in wallet.
        current_price: current price on the market
        orders: list of dictionnaries, each discribing a buy or a sell
    """

        def __init__(self, name, balance):
                self.name = name
                self.balance = float(balance)
                self.orders = []
                self.current_price = 0.0

        def print_gain(self):

                gain = None
                # get latest LIMIT_BUY
                for order in self.orders:
                        if order["OrderType"] == "LIMIT_BUY":
                                buy_price = float(order["PricePerUnit"])
                                gain = (self.current_price - buy_price) / buy_price * 100

                                if float(gain) > 0:
                                        print bcolors.OKGREEN + self.name + " : " + str(gain) + bcolors.ENDC
                                else :
                                        print bcolors.FAIL + self.name + " : " + str(gain) + bcolors.ENDC
                                break


# fetch data
response = bittrex.runner("getbalances", 0)
parsed_balance = json.loads(response)

response = bittrex.runner("getmarketsummaries", 0)
parsed_market = json.loads(response)

# get order history
response = bittrex.runner("getorderhistory", 0)
parsed_orderhistory = json.loads(response)

# create coinlist from balance
for x in parsed_balance["result"][:]:
        if x["Balance"] == 0.0 or x["Currency"] == "BTC":
                continue
        name = x["Currency"]
        balance = x["Balance"]
        print "adding " + name + " with balance " + str(balance)
        coinlist.append(coin(name, balance))

# fill coinlist with order history and current price - latest order is the first one
for x in coinlist:
        market_name = "BTC-" + x.name
        for coin in parsed_market["result"]:
                if market_name in coin["MarketName"]:
                        x.current_price = float(coin["Last"])
                        break

        for order in parsed_orderhistory["result"]:
                if market_name in order["Exchange"]:
                        print "found one order for", market_name, "of type", order["OrderType"]
                        x.orders.append(order)

for coin in coinlist:
         coin.print_gain()

####################################################
# print json.dumps(parsed, indent=4, sort_keys=True)
