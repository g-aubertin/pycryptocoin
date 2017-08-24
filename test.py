#!/usr/bin/env python

import bittrex, json, time

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
                for order in self.orders:
                        # get latest LIMIT_BUY
                        if order["OrderType"] == "LIMIT_BUY":
                                buy_price = float(order["PricePerUnit"])
                                gain = (self.current_price - buy_price) / buy_price * 100

                                if float(gain) > 0:
                                        print bcolors.OKGREEN + self.name + " : " + str(gain) + bcolors.ENDC
                                else :
                                        print bcolors.FAIL + self.name + " : " + str(gain) + bcolors.ENDC
                                break


def total_value(coinlist):
        total = 0.0
        for coin in coinlist:
                total = total + (coin.current_price * coin.balance)
        print "total value is " + str(total) + " BTC"

def fetch_exchange():
        # fetch data
        response = bittrex.runner("getbalances", 0)
        balance = json.loads(response)

        response = bittrex.runner("getmarketsummaries", 0)
        market = json.loads(response)

        # get order history
        response = bittrex.runner("getorderhistory", 0)
        orderhistory = json.loads(response)

        return balance, market, orderhistory

def create_coinlist():
        # get data from exchange
        balance, market, orderhistory = fetch_exchange()
        
        # create coinlist from balance
        for x in balance["result"]:
                if x["Balance"] == 0.0:
                        continue
                name = x["Currency"]
                balance = x["Balance"]
                coinlist.append(coin(name, balance))
                print "new coin", name, "created with balance", balance

        # fill coinlist with order history and current price - latest order is first in the list
        for x in coinlist:
                market_name = "BTC-" + x.name
                for new_coin in market["result"]:
                        if market_name in new_coin["MarketName"]:
                                x.current_price = float(new_coin["Last"])
                                break

                        for order in orderhistory["result"]:
                                if market_name in order["Exchange"]:
                                        x.orders.append(order)

def update_coinlist():
        # get data from exchange
        balance, market, orderhistory = fetch_exchange()

        # check for new coins
        for x in balance["result"]:
                name = x["Currency"]
                balance = x["Balance"]
                # test if no balance or already created coin object
                if balance == 0.0 :
                        print "no balance for", name
                        continue
                for x in coinlist:
                        if x.name == name:
                                print "coin", name, "already created"
                                continue
                coinlist.append(coin(name, balance))
                print "new coin", name, "has been added to the wallet"

        # sort list based on coin names
        coinlist.sort(key=lambda x: x.name)
        

if __name__ == '__main__':

        create_coinlist()

        while True:
                for x in coinlist:
                        x.print_gain()
                total_value(coinlist)
                update_coinlist()
                time.sleep(2)
        

####################################################
# print json.dumps(parsed, indent=4, sort_keys=True)
