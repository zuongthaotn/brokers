import pandas as pd
from pathlib import Path
import requests
import json

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
BANK_MARGIN_PORTFOLIO_ID = 123

LONG_DEAL_TYPE = "NB"
SHORT_DEAL_TYPE = "NS"
TRADING_FEE = 0.3


class Broker:
    def __init__(self, symbol):
        self.symbol = symbol
        self.bankMarginPortfolioId = BANK_MARGIN_PORTFOLIO_ID
        current_folder = str(Path(__file__).parent)
        f = open(current_folder + "/entrade/auth/jwt_token.txt", "r")
        bearer_token = f.read()
        f.close()
        if not bearer_token:
            raise Exception("Sorry, The bearer token file for Broker has problem!")
        else:
            self.bearer_token = bearer_token
        fa = open(current_folder + "/entrade/auth/credentials.json", "r")
        data = json.loads(fa.read())
        fa.close()
        if not data['entrade-auth']['account']['no']:
            raise Exception("Sorry, the DNSE account no not found!")
        else:
            self.investorId = data['entrade-auth']['account']['no']
        self.do_date = ''
        self.number_of_stocks = 0
        self.entry_price = 0
        self.exit_price = 0
        self.entry_time = ''
        self.is_long_open = False
        self.is_short_open = False
        self.history = []
        self._trades = pd.DataFrame(columns=("EntryTime", "EntryPrice", "ExitTime", "ExitPrice", "Type", "Profit"))
        self.mode = 'live'
        self.number_of_deal = 0
        self.qty = 0
        self.profit = 0
        self.total_profit = 0
        self.stoploss = 0
        self.force_stoploss = 0
        self.take_profit = 0
        self.deal_id = 0
        self.trigger = False
        self.logs = []

    def set_loan_package_id(self, new_id):
        self.loan_package_id = new_id

    def set_qty(self, new_qty):
        self.qty = new_qty

    def set_stoploss(self, price):
        self.stoploss = price

    def set_force_stoploss(self, price):
        self.force_stoploss = price

    def set_take_profit(self, price):
        self.take_profit = price

    def set_trigger(self, is_trigger):
        self.trigger = is_trigger

    def open_long_deal(self, price, order_type="LO"):
        self.trigger_before()
        if self.mode == 'live':
            self.number_of_stocks = self.qty
            self.entry_price = price
            self.is_long_open = True
            self.history.append('(Long) with price {} at {}'.format(price, self.do_date))
        deal_type = LONG_DEAL_TYPE
        self.open_deal(deal_type, price, order_type)
        self.trigger_after()

    def open_short_deal(self, price, order_type="LO"):
        self.trigger_before()
        if self.mode == 'live':
            self.number_of_stocks = self.qty
            self.entry_price = price
            self.is_short_open = True
            self.history.append('(Short) with price {} at {}'.format(price, self.do_date))
        deal_type = SHORT_DEAL_TYPE
        self.open_deal(deal_type, price, order_type)
        self.trigger_after()

    def close_all_open_deal(self, expected_price):
        self.trigger_before()
        # Close all open deal
        if self.has_opened_deal():
            self.qty = self.number_of_stocks
            if self.is_long_open:
                self.close_long_deal(expected_price, "MTL")
            elif self.is_short_open:
                self.close_short_deal(expected_price, "MTL")
        self.trigger_after()
        return False

    def close_long_deal(self, price, order_type="LO"):
        self.trigger_before()
        self.exit_price = price
        profit = price - self.entry_price - TRADING_FEE
        profit = round(profit, 1)
        self.profit = profit
        self.number_of_stocks = 0
        self.is_long_open = False
        if self.mode == 'live':
            self.history.append(
                '  --- (Close - Long) with price {} at {}, profit: {}'.format(price, self.do_date, profit))
        if self.mode == 'dev':
            self.total_profit += profit
            self.history.append(
                '  --- (Close - Long) with price {} at {}, profit: {}, total profit: {}'.format(price, self.do_date,
                                                                                                profit,
                                                                                                self.total_profit))
            self._trades.loc[len(self._trades)] = [self.entry_time, self.entry_price, self.do_date, price, "Long",
                                                   profit]
        deal_type = SHORT_DEAL_TYPE
        self.open_deal(deal_type, price, order_type)
        self.trigger_after()

    def close_short_deal(self, price, order_type="LO"):
        self.trigger_before()
        self.exit_price = price
        profit = self.entry_price - price - TRADING_FEE
        profit = round(profit, 1)
        self.profit = profit
        self.number_of_stocks = 0
        self.is_short_open = False
        if self.mode == 'live':
            self.history.append(
                '  --- (Close - Short) with price {} at {}, profit: {}'.format(price, self.do_date, profit))
        if self.mode == 'dev':
            self.total_profit += profit
            self.history.append(
                '  --- (Close - Short) with price {} at {}, profit: {}, total profit: {}'.format(price, self.do_date,
                                                                                                 profit,
                                                                                                 self.total_profit))
            self._trades.loc[len(self._trades)] = [self.entry_time, self.entry_price, self.do_date, price, "Short",
                                                   profit]
        deal_type = LONG_DEAL_TYPE
        self.open_deal(deal_type, price, order_type)
        self.trigger_after()

    def open_deal(self, deal_type, price, order_type="LO"):
        if not self.qty:
            self.qty = 1
        url = "https://services.entrade.com.vn/entrade-api/derivative/orders"
        header = {
            'User-Agent': USER_AGENT,
            'ContentType': 'application/json',
            'Authorization': 'Bearer ' + self.bearer_token
        }

        price = round(price, 1)

        data = {
            'symbol': self.symbol,
            'side': deal_type,
            'orderType': order_type,
            'price': price,
            'quantity': self.qty,
            'bankMarginPortfolioId': self.bankMarginPortfolioId,
            'investorId': self.investorId
        }

        res = requests.post(url, json=data, headers=header)
        if res.status_code != 200:
            # print(data)
            raise Exception(res.json())
        # print(f"Open deal status: {res.status_code}. ")

    def set_risk_reward(self):
        deal_id = self.deal_id
        risk = abs(self.entry_price - self.force_stoploss)
        reward = abs(self.take_profit - self.entry_price)
        if not deal_id or not risk or not reward:
            print("Error(*) while setting stoploss & take profit.")
            exit()
        url = "https://services.entrade.com.vn/entrade-derivative-deal-risk/pnl-configs/" + str(deal_id)
        header = {
            'User-Agent': USER_AGENT,
            'ContentType': 'application/json',
            'Trading-Token': self.trading_token,
            'Authorization': 'Bearer ' + self.bearer_token
        }

        data = {
            'takeProfitEnabled': True,
            'stopLossEnabled': True,
            'takeProfitStrategy': 'DELTA_PRICE',
            'takeProfitOrderType': 'FASTEST',
            'takeProfitDeltaPrice': reward,
            'stopLossStrategy': 'DELTA_PRICE',
            'stopLossOrderType': 'FASTEST',
            'stopLossDeltaPrice': risk
        }

        try:
            res = requests.post(url, json=data, headers=header)
            if res.status_code != 200:
                print(res.json())
        except:
            print("Error(**) while setting stoploss & take profit.")
            exit()

    def close_all_orders(self):
        url = "https://services.entrade.com.vn/entrade-order-service/derivative/orders?accountNo=" + self.account_no
        header = {
            'User-Agent': USER_AGENT,
            'ContentType': 'application/json',
            'Authorization': 'Bearer ' + self.bearer_token
        }

        res = requests.get(url, headers=header)
        if "orders" in res.json():
            orders = res.json()['orders']
            if len(orders) > 0:
                for order in orders:
                    if order['orderStatus'] == 'New' and order['id']:
                        self.cancel_order(order['id'])

    def cancel_order(self, id):
        url = "https://services.entrade.com.vn/entrade-order-service/derivative/orders/" + str(
            id) + "?accountNo=" + self.account_no
        header = {
            'User-Agent': USER_AGENT,
            'ContentType': 'application/json',
            'Trading-Token': self.trading_token,
            'Authorization': 'Bearer ' + self.bearer_token
        }
        try:
            requests.delete(url, headers=header)
        except:
            print("Error while open deal.")
            exit()

    def pull_deal_data(self):
        url = 'https://services.entrade.com.vn/entrade-derivative-core/deals?accountNo=' + self.account_no
        header = {
            'User-Agent': USER_AGENT,
            'ContentType': 'application/json', 'Authorization': 'Bearer ' + self.bearer_token}

        try:
            x = requests.get(url, headers=header)
        except:
            print("Error while pulling deal.")
            exit()
        data = []
        if "data" in x.json():
            data = x.json()['data']
        if len(data) > 0:
            for deal in data:
                self.number_of_deal += 1
                if deal['status'] == 'OPEN' and deal['costPrice'] and deal['loanPackageId'] == self.loan_package_id:
                    self.number_of_stocks = int(deal['openQuantity'])
                    self.entry_price = deal['costPrice']
                    self.deal_id = deal['id']
                    entry_time = pd.to_datetime(deal['modifiedDate']) + pd.DateOffset(hours=7)
                    entry_time = entry_time.strftime("%Y-%m-%d %H:%M:%S")
                    self.entry_time = entry_time
                    if deal['side'] == 'NB':
                        self.is_long_open = True
                    if deal['side'] == 'NS':
                        self.is_short_open = True
                    break
        else:
            self.number_of_stocks = 0
            self.is_long_open = False
            self.is_short_open = False
            self.entry_time = ''

    def has_opened_deal(self):
        return True if self.number_of_stocks > 0 else False

    def trigger_before(self):
        if not self.trigger:
            return
        order_type = "Long" if self.is_long_open else ("Short" if self.is_short_open else "None")
        msg = f"Before. Ordered qty: {self.number_of_stocks}, order_type: {order_type}, " \
              f"entry_price: {self.entry_price}, entry_time: {self.entry_time}"
        self.log(msg)

    def trigger_after(self):
        if not self.trigger:
            return
        msg = f"After. Ordered qty: {self.number_of_stocks}."
        self.log(msg)

    def log(self, msg):
        if self.mode == 'live':
            self.logs.append(msg)
