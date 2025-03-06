#!/bin/bash
DIR=$(cd "$(dirname "$0")"; pwd)
cd $DIR
cd ..
#
venv/bin/python brockers/dnse/auth/get_jwt_token.py
#
sleep 5
#
venv/bin/python brockers/dnse/auth/request_email_otp.py
#
sleep 55
#
venv/bin/python brockers/dnse/gmail/get_otp.py
#
venv/bin/python brockers/dnse/auth/get_trading_token.py