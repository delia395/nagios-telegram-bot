#!/usr/bin/env/python
# -*- coding: utf-8 -*-

import logging
import sys
import telepot
import argparse
import urllib3

from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup


debug = True

# Insert the the user IDs here in the list. ECO is for the on call one
users=[ ]
eco=[]

logger = logging.getLogger('bot')
logger.setLevel(logging.INFO)
log_format = logging.Formatter('%(asctime)s %(name)s %(levelname)-8s %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)

parser = argparse.ArgumentParser(description='Process Nagios Alert.')
parser.add_argument("-t", "--type")
parser.add_argument("-n", "--name")
parser.add_argument("-a", "--host")
parser.add_argument("-f", "--fullname")
parser.add_argument("-i", "--ip")
parser.add_argument("-s", "--state")
parser.add_argument("-d", "--datetime")
parser.add_argument("-o", "--output")
parser.add_argument("-x", "--xtext")
parser.add_argument("-e", action='store_true')
args = parser.parse_args()


ALMMSG="-- Nagios Alert -- \n\nNotification Type: {}\nService: {}\nHost: {}\nIP Addr: {}\nState: {}\nTime: {}\n\nAdditional Info: {}".format(args.type, args.name, args.host, args.ip, args.state, args.datetime, args.output)

### If you need proxy, uncomment the following part
#proxy_url = "<URL>:<PORT>"
#telepot.api._pools = {'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),}
#telepot.api._onetime_pool_spec = (urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))

### Insert your token here. Don't expose your token to others!
bot = telepot.Bot('XXXXXXXXX:EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')

if args.xtext:
    msg = bot.getMe()
    logger.info("BEGIN: getMe(): {!r}".format(msg))
    ALMMSG = args.xtext

if args.e:
    users = eco[:]
    ALMMSG = "ECO ALERT(24x7) \n"+ALMMSG

keyboard=None
if args.fullname and args.type=="PROBLEM" :
    callback_info="disable;{};{}".format(args.fullname,args.name)
    my_inline_keyboard = [[ InlineKeyboardButton(text="Disable this notification", callback_data=callback_info) ]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=my_inline_keyboard)


for one in users:
    logger.info("Notification to user {}. Msg: {}".format(one, ALMMSG))
    if keyboard:
        bot.sendMessage(one, ALMMSG, reply_markup=keyboard)
    else:
        bot.sendMessage(one, ALMMSG)
