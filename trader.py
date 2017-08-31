#!/usr/bin/env python

import bittrex, json, time
import ConfigParser

blacklist = []

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
        orders: order history
        open_orders:
    """

        def __init__(self, name, balance):
                self.name = name
                self.balance = float(balance)
                self.orders = []
                self.last_price = 0.0
                self.open_orders = []

        def print_gain(self):
                for order in self.orders:
                        # get latest LIMIT_BUY
                        if order["OrderType"] == "LIMIT_BUY":
                                buy_price = float(order["PricePerUnit"])
                                gain = (self.last_price - buy_price) / buy_price * 100

                                if float(gain) > 0:
                                        print bcolors.OKGREEN + self.name + " : " + str(gain) + bcolors.ENDC
                                else :
                                        print bcolors.FAIL + self.name + " : " + str(gain) + bcolors.ENDC
                                return gain


class bittrex_wallet:
        """bittrex wallet

    Attributes:
        coinlist: list of owned coins
        balance : coin balance for all coins supported by the exchange
        marketsummaries: market summary for all coins supported by the exchange
        orderhistory: past orders
        openorders: on-going orders
    """

        def __init__(self):
                self.coinlist = []
                self.balance = []
                self.marketsummaries = []
                self.orderhistory = []
                self.openorders = []

                self.fetch_data()

                # create coinlist from balance
                for x in self.balance["result"]:
                        if x["Balance"] == 0.0 or x["Currency"] in blacklist:
                                continue
                        name = x["Currency"]
                        balance = x["Balance"]
                        self.coinlist.append(coin(name, balance))
                        print "new coin", name, "created with balance", balance

                # fill coinlist with order history, open orders and last price
                # latest order comes first in the list
                for newcoin in self.coinlist:

                        if newcoin.name == "BTC":
                                newcoin.last_price = 1
                                continue

                        market_name = "BTC-" + newcoin.name

                        for entry in self.market["result"]:
                                if market_name in entry["MarketName"]:
                                        newcoin.last_price = float(entry["Last"])
                                        break

                        for order in self.orderhistory["result"]:
                                if market_name in order["Exchange"]:
                                        newcoin.orders.append(order)

                        for order in self.openorders["result"]:
                                if market_name in order["Exchange"]:
                                        newcoin.open_orders.append(order)

        # get data from exchange
        def fetch_data(self):
                start_time = time.time()

                response = bittrex.runner("getbalances", 0)
                self.balance = json.loads(response)

                response = bittrex.runner("getmarketsummaries", 0)
                self.market = json.loads(response)

                response = bittrex.runner("getorderhistory", 0)
                self.orderhistory = json.loads(response)

                response = bittrex.runner("getopenorders", 0)
                self.openorders = json.loads(response)

                end_time = time.time()
                print("fetch_exchange execution time : %g seconds" % (end_time - start_time))


        # update coinlist
        def update(self):

                self.fetch_data()

                # check for new coins
                for x in self.balance["result"]:
                        name = x["Currency"]
                        balance = x["Balance"]
                        # test if no balance or already created coin object
                        if balance == 0.0 or name in blacklist:
                                continue
                        for x in self.coinlist:
                                if x.name == name:
                                        x.balance = float(balance)
                                        break
                        else:
                                self.coinlist.append(coin(name, balance))
                                print "new coin", name, "has been added to the wallet"

                # update current price
                for x in self.coinlist:

                        if x.name == "BTC":
                                x.last_price = 1
                                continue

                        market_name = "BTC-" + x.name

                        for entry in self.market["result"]:
                                if market_name in entry["MarketName"]:
                                        x.last_price = float(entry["Last"])
                                        print "updating last price for", market_name, "to ", x.last_price
                                        break


                        # sort list based on coin names
                        self.coinlist.sort(key=lambda x: x.name)


        # calculate current wallet value in BTC
        def value(self):
                total = 0.0
                for coin in self.coinlist:
                        total = total + (coin.last_price * coin.balance)
                print "total value is " + str(total) + " BTC"

        # print gains for each coin with positive balance
        def summary(self):
                for coin in self.coinlist:
                        coin.print_gain()


def autotrade(tradelist, rule_low, rule_high):
        print""
        print"########## AUTOTRADE ##########"

        for coin in coinlist:
                if coin.name in tradelist:
                        gain = coin.print_gain()
                        if gain < rule_low:
                                print "coin", coin.name, "is below 5%, selling"
                        if gain > rule_high:
                                print "coin", coin.name, "is above 10%, selling"

        print"######## END AUTOTRADE ########"
        print ""

if __name__ == '__main__':

        config = ConfigParser.ConfigParser()
        config.read('config.ini')

        blacklist = config.get('ignore', 'currencies')
        blacklist = blacklist.split(',')
        print "blacklist: ", blacklist

        tradelist = config.get('autotrade', 'currencies')
        tradelist = tradelist.split(',')
        print "tradelist: ", tradelist

        rule_low = float(config.get('rules', 'low'))
        rule_high = float(config.get('rules', 'high'))
        print "rules - low:", rule_low, ", high:", rule_high

        wallet = bittrex_wallet()

        while True:

                wallet.update()
                wallet.summary()
                wallet.value()

                time.sleep(60)

####################################################
# print json.dumps(parsed, indent=4, sort_keys=True)
