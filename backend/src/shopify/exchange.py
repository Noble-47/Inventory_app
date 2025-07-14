from exchange import Exchange

exchange = Exchange("shopify")

exchange.establish_channel("shops_notifications")
exchange.establish_channel("settings_notifications")
