#!/usr/bin/env python

import crypto
import bittrex, json, time
import ConfigParser

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

        '''
        
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

        wallet = crypto.bittrex_wallet(blacklist)

        while True:

                wallet.summary()
                wallet.value()
                print""
                time.sleep(30)
                wallet.update()
        '''

        # API v2 test

        wallet = crypto.bittrex_wallet(None, True)
        '''
        response = bittrex.runner("getcandles", "BTC-ETH", "thirtyMin")
        parsed = json.loads(response)
        print json.dumps(parsed, indent=4, sort_keys=True)

        response = bittrex.runner("getmarketsummary", "BTC-ETH", 0)
        parsed = json.loads(response)
        print json.dumps(parsed, indent=4, sort_keys=True)

        response = bittrex.runner("getlastcandle", "BTC-ETH", "thirtyMin")
        parsed = json.loads(response)
        print json.dumps(parsed, indent=4, sort_keys=True)
        '''


####################################################
# print json.dumps(parsed, indent=4, sort_keys=True)
