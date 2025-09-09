from brokers.entrade import Broker

if __name__ == "__main__":
    ticker = "VN30F2509"
    broker = Broker(ticker)
    # broker.open_short_deal(1830)
    broker.close_all_orders()
