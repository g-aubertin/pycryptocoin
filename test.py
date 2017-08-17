#!/usr/bin/env python

import bittrex, json

print bittrex.API_KEY
print bittrex.API_SECRET

class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

# simple test to get balance
response = bittrex.runner("getbalances", 0)
parsed_balance = json.loads(response)

response = bittrex.runner("getmarketsummary", "BTC-ARK")
parsed_summary = json.loads(response)

response = bittrex.runner("getorderhistory", 0)
parsed_orderhistory = json.loads(response)

for x in parsed_balance["result"][:]:
    if x["Currency"] == "BTC" or x["Balance"] == 0.0:
        continue
    response = bittrex.runner("getmarketsummary", "BTC-" + x["Currency"])
    parsed_market = json.loads(response)
    response = bittrex.runner("getorderhistory", "BTC-" + x["Currency"])
    parsed_order = json.loads(response)

    print "COIN :", x["Currency"], "BALANCE :", x["Balance"]
    print "current price :", parsed_market["result"][0]["Last"]

    try:
        buy_price = str(parsed_order["result"][0]["PricePerUnit"])
        evolution = str((parsed_market["result"][0]["Last"] - parsed_order["result"][0]["PricePerUnit"]) / parsed_order["result"][0]["PricePerUnit"] * 100)

        print "buy price : " + buy_price
        if float(evolution) > 0:
            print bcolors.OKGREEN + "gain :" + evolution + bcolors.ENDC
        else :
            print bcolors.FAIL + "gain :" + evolution + bcolors.ENDC
            
    except:
            print "no buy price"
    print "\n"

# todo :
# - quick display (oneliner) of each owned coin
# - get last order for each owned coin
# - compare current price and buy price
# - display variation

####################################################
# print json.dumps(parsed, indent=4, sort_keys=True)
