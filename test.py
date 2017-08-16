#!/usr/bin/env python

import bittrex, json

print bittrex.API_KEY
print bittrex.API_SECRET

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
        parsed_order["result"][0]["PricePerUnit"]
        print  "buy price :", parsed_order["result"][0]["PricePerUnit"]
        print "evolution :", (parsed_market["result"][0]["Last"] - parsed_order["result"][0]["PricePerUnit"]) / parsed_order["result"][0]["PricePerUnit"] * 100
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
