# DNSE broker


## Required Google credentials for Gmail
Read Google API to get credentials.json & token.json
https://developers.google.com/gmail/api/guides

Read DNSE Lightspeed API
https://hdsd.dnse.com.vn/san-pham-dich-vu/lightspeed-api/ii.-trading-api

## setup cron
crontab -e
add
40 8 * * 1,2,3,4,5 bash /home//algo-stocks/brokers/dnse/daily_token.sh > null

## Use
from brokers.dnse import Broker

if __name__ == "__main__":
    ticker = "VN30F2503"
    broker = Broker(ticker)
    broker.pull_deal_data()
    broker.open_long_deal(expected_price, order_type="MTL")
    
    broker.open_short_deal(expected_price, order_type="MTL")
    
    broker.set_force_stoploss(1364)
    broker.set_take_profit(1390)
    broker.set_risk_reward()

    broker.close_all_open_deal(current_price)
