import NBP

fee_currencies = ["PLN", "EUR", "USD"]


def find_online_markets(API1, API2):
    API_with_less_markets = API1.request_market_data()
    API_with_more_markets = API2.request_market_data()
    online_markets = []
    if len(API_with_more_markets) < len(API_with_less_markets):
        temp = API_with_less_markets
        API_with_less_markets = API_with_more_markets
        API_with_more_markets = temp
    for market in API_with_less_markets:
        if market in API_with_more_markets:
            online_markets.append(market)
    return online_markets


def get_value_user_curr(init_currency: str, target_currency: str, money: float):
    if init_currency == target_currency:
        return money
    target_currency_value_of_money = money
    if init_currency != "PLN":
        money_in_PLN = NBP.get_avg_exchange_rate(init_currency) * money
        target_currency_value_of_money = money_in_PLN
    if target_currency != "PLN":
        money_in_target_currency = target_currency_value_of_money / NBP.get_avg_exchange_rate(target_currency)
        target_currency_value_of_money = money_in_target_currency
    return target_currency_value_of_money


def get_multiplier(API, market_quote_curr: str):
    API_fee_currency = API.get_fee_currency()
    if market_quote_curr != API_fee_currency and market_quote_curr not in fee_currencies:
        return API.value_of_curr_in_api_curr(market_quote_curr)
    elif market_quote_curr != API_fee_currency and market_quote_curr in fee_currencies:
        return get_value_user_curr(market_quote_curr, API_fee_currency, 1)
    else:
        return 1


def take_bid_offers(buy_offers, sell_offers, user_amount_of_curr, multiplier, API, user_volume_on_api):
    money_from_sell = 0
    avg_rate_temp = 0
    number_of_iterations = 0
    for buy_offer in list(buy_offers):
        buy_quantity = float(buy_offer["quantity"])
        buy_rate = float(buy_offer["rate"])
        sell_fees = API.get_maker_taker_fee(user_volume_on_api)
        transaction_volume = buy_quantity * buy_rate
        if user_amount_of_curr < buy_quantity:
            lowest_ask_rate = float(sell_offers[0]["rate"])
            transaction_volume = user_amount_of_curr * lowest_ask_rate
            transaction_cost = sell_fees["maker_fee"] * transaction_volume
            user_volume_on_api += (transaction_volume * multiplier)
            money_from_sell += (transaction_volume - transaction_cost)
            avg_rate_temp += lowest_ask_rate
            number_of_iterations += 1
            break
        transaction_cost = sell_fees["taker_fee"] * transaction_volume
        user_volume_on_api += (transaction_volume * multiplier)
        money_from_sell += (transaction_volume - transaction_cost)
        user_amount_of_curr -= buy_quantity
        avg_rate_temp += buy_rate
        buy_offers.remove(buy_offer)
        number_of_iterations += 1
    if number_of_iterations == 0:
        avg_rate = 0
    else:
        avg_rate = avg_rate_temp / number_of_iterations
    return money_from_sell, user_volume_on_api, avg_rate


def sell_currency(amount_of_currency: float, currency: str, init_user_api_volume: float, user_currency: str, API):
    user_amount_of_currency = amount_of_currency
    user_volume_on_api = init_user_api_volume
    market = (currency, API.get_fee_currency())
    online_markets = API.request_market_data()
    market_found = False
    if market in online_markets:
        market_found = True
    else:
        for online_market in online_markets:
            if online_market[0] == market[0] and market[1] in fee_currencies:
                market = online_market
                market_found = True
    if market_found is False:
        return 0, user_volume_on_api, 0
    else:
        buy_offers = API.request_bids_and_asks(market)["bid"]
        sell_offers = API.request_bids_and_asks(market)["ask"]
        if buy_offers is None or buy_offers is []:
            return 0, user_volume_on_api, API.get_ticker_rate()
    sell_offers.sort(key=lambda offer: float(offer["rate"]))
    buy_offers.sort(key=lambda offer: float(offer["rate"]), reverse=True)
    multiplier = get_multiplier(API, market[1])
    sell_data = take_bid_offers(buy_offers, sell_offers, user_amount_of_currency, multiplier, API, user_volume_on_api)
    money_from_sell = sell_data[0]
    user_volume_on_api = sell_data[1]
    avg_rate = sell_data[2]
    earned_money = money_from_sell * multiplier
    if API.get_fee_currency() != user_currency:
        earned_money = get_value_user_curr(API.get_fee_currency(), user_currency, money_from_sell)
    return earned_money, user_volume_on_api, avg_rate


def find_arbitrage(API_BUY, init_api1_volume: float, API_SELL, init_api2_volume: float, market: tuple[str, str]):
    volume_on_api1 = init_api1_volume
    volume_on_api2 = init_api2_volume
    buy_multiplier = get_multiplier(API_BUY, market[1])
    sell_multiplier = get_multiplier(API_SELL, market[1])
    sell_offers = API_BUY.request_bids_and_asks(market)["ask"]
    sell_offers.sort(key=lambda offer: float(offer["rate"]))
    buy_offers = API_SELL.request_bids_and_asks(market)["bid"]
    buy_offers.sort(key=lambda offer: float(offer["rate"]), reverse=True)
    earned_money = 0
    avg_rate = 0
    for sell_offer in sell_offers:
        fees_buy = API_BUY.get_maker_taker_fee(volume_on_api1)
        sell_quantity = float(sell_offer["quantity"])
        buy_volume = sell_quantity * float(sell_offer["rate"])
        transaction_cost = fees_buy["taker_fee"] * sell_quantity
        withdrawn_crypto = sell_quantity - transaction_cost - API_BUY.get_withdrawal_list()[market[0]]
        money_to_sell = withdrawn_crypto
        sell_data = take_bid_offers(buy_offers, sell_offers, money_to_sell, sell_multiplier, API_SELL, volume_on_api2)
        money_from_sell = sell_data[0]
        transaction_profit = money_from_sell - buy_volume
        if transaction_profit > 0:
            # print(f"SUCCESS! {transaction_profit} in {market[0]}-{market[1]}")
            volume_on_api1 += (buy_volume * buy_multiplier)
            volume_on_api2 = sell_data[1]
            avg_rate = sell_data[2]
            earned_money += transaction_profit
        else:
            # print(f"{transaction_profit} in {market[0]}-{market[1]}")
            break
    return earned_money, volume_on_api1, volume_on_api2, avg_rate, API_BUY.get_name(), API_SELL.get_name()


def arbitrage_book(API1, user_volume_on_API1, API2, user_volume_on_API2, markets):
    online_markets = find_online_markets(API1, API2)
    wanted_markets = []
    for market in markets:
        if market in online_markets:
            wanted_markets.append(market)
    arbitrage_dictionary = dict()
    for market in wanted_markets:
        arbitrage_dictionary[market] = find_arbitrage(API1, user_volume_on_API1, API2, user_volume_on_API2, market)
    arbitrage_list = sorted(arbitrage_dictionary.items(), key=lambda market_arb: market_arb[1], reverse=True)
    return arbitrage_list
