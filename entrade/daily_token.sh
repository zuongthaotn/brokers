#!/bin/bash
DIR=$(cd "$(dirname "$0")"; pwd)
cd $DIR
cd ../..
#
venv/bin/python brokers/entrade/auth/get_jwt_token.py
#