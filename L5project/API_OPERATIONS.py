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
        money_in_target_currency = money / NBP.get_avg_exchange_rate(target_currency)
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
    last_rate = 0
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
            last_rate = lowest_ask_rate
            break
        transaction_cost = sell_fees["taker_fee"] * transaction_volume
        user_volume_on_api += (transaction_volume * multiplier)
        money_from_sell += (transaction_volume - transaction_cost)
        user_amount_of_curr -= buy_quantity
        last_rate = buy_rate
        buy_offers.remove(buy_offer)
    return money_from_sell, user_volume_on_api, last_rate


def sell_currency(init_user_money: float, to_sell_currency: str, init_user_api_volume: float, user_currency: str, API):
    user_amount_of_currency = init_user_money
    user_volume_on_api = init_user_api_volume
    market = (to_sell_currency, API.get_fee_currency())
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
            return 0, user_volume_on_api, 0
    sell_offers.sort(key=lambda offer: float(offer["rate"]))
    buy_offers.sort(key=lambda offer: float(offer["rate"]), reverse=True)
    multiplier = get_multiplier(API, market[1])
    sell_data = take_bid_offers(buy_offers, sell_offers, user_amount_of_currency, multiplier, API, user_volume_on_api)
    money_from_sell = sell_data[0]
    user_volume_on_api = sell_data[1]
    last_rate = sell_data[2]
    earned_money = money_from_sell * multiplier
    if API.get_fee_currency() != user_currency:
        earned_money = get_value_user_curr(API.get_fee_currency, user_currency, money_from_sell)
    return earned_money, user_volume_on_api, last_rate


def find_arbitrage(API_BUY, init_user_api1_volume: float, API_SELL, init_user_api2_volume: float,
                   market: tuple[str, str]):
    user_volume_on_api1 = init_user_api1_volume
    user_volume_on_api2 = init_user_api2_volume
    api_buy_vol_multiplier = get_multiplier(API_BUY, market[1])
    api_sell_vol_multiplier = get_multiplier(API_SELL, market[1])
    sell_offers = API_BUY.request_bids_and_asks(market)["ask"]
    sell_offers.sort(key=lambda offer: float(offer["rate"]))
    buy_offers = API_SELL.request_bids_and_asks(market)["bid"]
    buy_offers.sort(key=lambda offer: float(offer["rate"]), reverse=True)
    earned_money = 0
    last_rate = 0
    for sell_offer in sell_offers:
        fees_buy = API_BUY.get_maker_taker_fee(user_volume_on_api1)
        sell_quantity = float(sell_offer["quantity"])
        buy_volume = sell_quantity * float(sell_offer["rate"])
        transaction_cost = fees_buy["taker_fee"] * sell_quantity
        withdrawn_crypto = sell_quantity - transaction_cost - API_BUY.get_withdrawal_list()[market[0]]
        remaining_money = withdrawn_crypto
        sell_data = take_bid_offers(buy_offers, sell_offers, remaining_money, api_sell_vol_multiplier, API_SELL,
                                    user_volume_on_api2)
        money_from_sell = sell_data[0]
        transaction_profit = money_from_sell - buy_volume
        if transaction_profit > 0:
            print(f"SUCCESS! {transaction_profit} in {market[0]}-{market[1]}")
            user_volume_on_api1 += (buy_volume * api_buy_vol_multiplier)
            user_volume_on_api2 = sell_data[1]
            last_rate = sell_data[2]
            earned_money += transaction_profit
        else:
            print(f"{transaction_profit} in {market[0]}-{market[1]}")
            break
    return earned_money, user_volume_on_api1, user_volume_on_api2, last_rate


def arbitrage_book(API1, user_volume_on_API1, API2, user_volume_on_API2):
    online_markets = find_online_markets(API1, API2)
    arbitrage_dictionary = dict()
    for market in online_markets:
        arbitrage_dictionary[market] = find_arbitrage(API1, user_volume_on_API1, API2, user_volume_on_API2, market)
    arbitrage_list = sorted(arbitrage_dictionary.items(), key=lambda market_arb: market_arb[1], reverse=True)
    return arbitrage_list
