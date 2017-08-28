#!/usr/bin/env python

import bittrex, json, time
import ConfigParser

coinlist = []
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
                self.current_price = 0.0
                self.open_orders = []

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
                                return gain



                        
def total_value(coinlist):
        total = 0.0
        for coin in coinlist:
                total = total + (coin.current_price * coin.balance)
        print "total value is " + str(total) + " BTC"

def fetch_exchange():

        start_time = time.time()
        
        # fetch data
        response = bittrex.runner("getbalances", 0)
        balance = json.loads(response)

        response = bittrex.runner("getmarketsummaries", 0)
        market = json.loads(response)

        # get order history
        response = bittrex.runner("getorderhistory", 0)
        orderhistory = json.loads(response)

        # get open orders
        response = bittrex.runner("getopenorders", 0)
        openorders = json.loads(response)

        end_time = time.time()
        print("fetch_exchange execution time : %g seconds" % (end_time - start_time))


        return balance, market, orderhistory, openorders

def create_coinlist():
        # get data from exchange
        balance, market, orderhistory, openorders = fetch_exchange()

        start_time = time.time()
        
        # create coinlist from balance
        for x in balance["result"]:
                if x["Balance"] == 0.0 or x["Currency"] in blacklist:
                        continue
                name = x["Currency"]
                balance = x["Balance"]
                coinlist.append(coin(name, balance))
                print "new coin", name, "created with balance", balance

        # fill coinlist with order history, open orders and current price - latest order is first in the list
        for x in coinlist:
                market_name = "BTC-" + x.name
#                print "filling for", market_name

                for new_coin in market["result"]:
                        if market_name in new_coin["MarketName"]:
                                x.current_price = float(new_coin["Last"])
                                break

                for order in orderhistory["result"]:
                        if market_name in order["Exchange"]:
#                                print "adding new orderhistory"
                                x.orders.append(order)

                for order in openorders["result"]:
                        if market_name in order["Exchange"]:
                                x.open_orders.append(order)
 #                               print "adding open order"

        end_time = time.time()
        print("coinlist creation execution time : %g seconds" % (end_time - start_time))


def update_coinlist():
        # get data from exchange
        balance, market, orderhistory, openorders = fetch_exchange()

        start_time = time.time()
        
        # check for new coins
        for x in balance["result"]:
                name = x["Currency"]
                balance = x["Balance"]
                # test if no balance or already created coin object
                if balance == 0.0 or name in blacklist:
                        #print "no balance for", name
                        continue
                for x in coinlist:
                        if x.name == name:
                                #print "coin", name, "already created, updating only balance"
                                x.balance = float(balance)
                                break
                else:
                        coinlist.append(coin(name, balance))
                        print "new coin", name, "has been added to the wallet"

        # sort list based on coin names
        coinlist.sort(key=lambda x: x.name)

        end_time = time.time()
        print("coinlist update execution time : %g seconds" % (end_time - start_time))



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

        create_coinlist()

        while True:

                update_coinlist()

                for x in coinlist:
                        x.print_gain()
                total_value(coinlist)

                autotrade(tradelist, rule_low, rule_high)

                time.sleep(60)

####################################################
# print json.dumps(parsed, indent=4, sort_keys=True)
