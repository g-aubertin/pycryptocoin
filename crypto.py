import time, json, bittrex

# iteration rate in seconds
tick = 30

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
        open_orders: on-going orders
        summaries: market summaries
    """

        def __init__(self, name, balance):
                self.name = name
                self.balance = float(balance)
                self.orders = []
                self.open_orders = []
                self.coin_summaries = []

        def print_gain(self):
                for order in self.orders:
                        # get latest LIMIT_BUY
                        if order["OrderType"] == "LIMIT_BUY":
                                buy_price = float(order["PricePerUnit"])
                                gain = (float(self.coin_summaries[0]["Last"]) - buy_price) / buy_price * 100

                                if float(gain) > 0:
                                        print bcolors.OKGREEN + self.name + " : " + str(gain) + bcolors.ENDC
                                else :
                                        print bcolors.FAIL + self.name + " : " + str(gain) + bcolors.ENDC
                                return gain
                        
#        def print_trend(self):
                # calculate evolution based on value 5 minutes if available
                # otherwise, calculate with older value.
                # tick value is used to decide which summary to use to get to 5 minutes
#                iterations = 300 / tick
#                last_price = float(self.coin_summaries[0]["Last"])
#                print "current price:", last_price
                
#                if len(self.coin_summaries) < iterations:
#                        base_price = float(self.coin_summaries[-1]["Last"])

#                else:
#                        base_price = float(self.coin_summaries[iterations]["Last"])

 #               print "base price:", base_price

#                evolution = (last_price - base_price) / base_price * 100
 #               if float(evolution) > 0:
 #                       print bcolors.OKGREEN + self.name + " evolution over 5 minutes : " + str(evolution) + bcolors.ENDC
#                else :
                        #print bcolors.FAIL + self.name + " evolution over 5 minutes : " + str(evolution) + bcolors.ENDC
                        
class bittrex_wallet:
        """bittrex wallet

    Attributes:
        coinlist: list of owned coins
        balance : coin balance for all coins supported by the exchange
        marketsummaries: market summary for all coins supported by the exchange
        orderhistory: past orders
        openorders: on-going orders
    """

        def __init__(self, blacklist):
                self.coinlist = []
                self.balance = []
                self.marketsummaries = []
                self.orderhistory = []
                self.openorders = []
                self.blacklist = blacklist

                self.fetch_data()

                # create coinlist from balance
                for x in self.balance["result"]:
                        if x["Balance"] == 0.0 or x["Currency"] in self.blacklist:
                                continue
                        name = x["Currency"]
                        balance = x["Balance"]
                        self.coinlist.append(coin(name, balance))
                        print "new coin", name, "created with balance", balance

                # fill coinlist with order history, open orders and market summary
                # for orders and history, latest comes first in the list
                for newcoin in self.coinlist:

#                        if newcoin.name == "BTC":
#                                newcoin.last_price = 1
#                                continue

                        market_name = "BTC-" + newcoin.name
                        
                        for entry in self.market["result"]:
                                if market_name in entry["MarketName"]:
                                        newcoin.coin_summaries.append(entry)
                                        print "adding new market entry:"
                                        print json.dumps(entry, indent=4, sort_keys=True)

                        for order in self.orderhistory["result"]:
                                if market_name in order["Exchange"]:
                                        newcoin.orders.append(order)

                        for order in self.openorders["result"]:
                                if market_name in order["Exchange"]:
                                        newcoin.open_orders.append(order)

                # debug
                for newcoin in self.coinlist:
                        print "##### name: ", newcoin.name
                        print "balance:", newcoin.balance
                        print "summaries:"
                        print json.dumps(newcoin.coin_summaries, indent=4, sort_keys=True)
                        print "=== executed orders:"  
                        print json.dumps(newcoin.orders, indent=4, sort_keys=True)
                        print "=== open orders:"  
                        print json.dumps(newcoin.open_orders, indent=4, sort_keys=True)
                        
                                        
        # update coinlist
        def update(self):

                self.fetch_data()

                # check for new coins
                for x in self.balance["result"]:
                        name = x["Currency"]
                        balance = x["Balance"]
                        # test if no balance or already created coin object
                        if balance == 0.0 or name in self.blacklist:
                                continue
                        for x in self.coinlist:
                                if x.name == name:
                                        x.balance = float(balance)
                                        break
                        else:
                                self.coinlist.append(coin(name, balance))
                                print "new coin", name, "has been added to the wallet"
                                

                # check for removed coins
                for entry in self.coinlist[:]:
                        for x in self.balance["result"]:
                                name = x["Currency"]
                                balance = x["Balance"]
                                if name == entry.name and balance == 0.0:
                                        print "removing", name, "from coinlist"
                                        coinlist.remove(entry)
                
                # coinlist is now up-to-date, updating attributes
                for newcoin in self.coinlist:

                        market_name = "BTC-" + newcoin.name

                        for entry in self.market["result"]:
                                if market_name in entry["MarketName"]:
                                        newcoin.coin_summaries.append(entry)

                        del newcoin.orders[:]
                        for order in self.orderhistory["result"]:
                                if market_name in order["Exchange"]:
                                        newcoin.orders.append(order)

                        del newcoin.open_orders[:]
                        for order in self.openorders["result"]:
                                if market_name in order["Exchange"]:
                                        newcoin.open_orders.append(order)
                
                # sort list based on coin names
                self.coinlist.sort(key=lambda x: x.name)

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

        # calculate current wallet value in BTC
        def value(self):
                total = 0.0
                for coin in self.coinlist:
                        total = total + (float(coin.coin_summaries[0]["Last"]) * coin.balance)
                print "total value is " + str(total) + " BTC"

        # print gains for each coin with positive balance
        def summary(self):
                print "### current gains ###"
                for coin in self.coinlist:
                        coin.print_gain()
#                        coin.print_trend()
                print "#####################"
