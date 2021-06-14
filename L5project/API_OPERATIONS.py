import NBP


def find_online_markets(API1, API2):
    API1_markets = API1.request_market_data()
    API2_markets = API2.request_market_data()
    API_with_less_markets = API1_markets
    API_with_more_markets = API2_markets
    online_markets = []

    if len(API2_markets) < len(API1_markets):
        API_with_less_markets = API2_markets
        API_with_more_markets = API1_markets

    for market in API_with_less_markets:
        if market in API_with_more_markets:
            online_markets.append(market)

    return online_markets


def get_value_in_user_currency(init_currency: str, target_currency: str, money: float):
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


def sell_currency_on_api(init_val_user_amount_of_currency: float, currency_to_sell: str,
                         init_val_user_overall_volume_on_api: float, user_default_currency: str, API_SELL):
    user_volume_on_api = init_val_user_overall_volume_on_api
    user_amount_of_currency = init_val_user_amount_of_currency
    user_money_earned = 0
    market = (currency_to_sell, API_SELL.get_fee_currency())
    bids_asks_data = API_SELL.request_bids_and_asks(market)
    bids = bids_asks_data["bid"].sort(key=lambda data: data["rate"], reverse=True)

    for bid in bids:
        fees = API_SELL.get_maker_taker_fee(user_volume_on_api)
        volume_of_transaction = float(bid["quantity"]) * float(bid["rate"])
        if user_amount_of_currency < float(bid["quantity"]):
            volume_of_transaction = user_amount_of_currency * float(bid["rate"])
            cost_of_transaction = fees["maker_fee"] * volume_of_transaction
            user_volume_on_api += volume_of_transaction
            user_money_earned += (volume_of_transaction - cost_of_transaction)
            break
        cost_of_transaction = fees["taker_fee"] * volume_of_transaction
        user_volume_on_api += volume_of_transaction
        user_money_earned += (volume_of_transaction - cost_of_transaction)
        user_amount_of_currency -= float(bid["quantity"])

    earned_money = user_money_earned
    if API_SELL.get_fee_currency() != user_default_currency:
        earned_money = get_value_in_user_currency(API_SELL.get_fee_currency, user_default_currency,
                                                  user_money_earned)
    return earned_money


def find_arbitrage(API_BUY, init_user_volume_on_api1: float, API_SELL, init_user_volume_on_api2: float,
                   market: tuple[str, str]):
    fee_currencies = ["PLN", "EUR", "USD"]
    user_volume_on_api1 = init_user_volume_on_api1
    user_volume_on_api2 = init_user_volume_on_api2
    bids_asks_api_buy_from = API_BUY.request_bids_and_asks(market)
    bids_asks_api_sell_to = API_SELL.request_bids_and_asks(market)
    sell_offers = sorted(bids_asks_api_buy_from["ask"], key=lambda bid: float(bid.get("rate")))
    buy_offers = sorted(bids_asks_api_sell_to["bid"], key=lambda bid: float(bid.get("rate")), reverse=True)
    market_base_curr = market[0]
    market_quote_curr = market[1]
    volume_api_buy_multiplier = 1
    volume_api_sell_multiplier = 1
    earned_money = 0
    API_BUY_fee_currency = API_BUY.get_fee_currency()
    API_SELL_fee_currency = API_SELL.get_fee_currency()

    if market_quote_curr != API_BUY_fee_currency and market_quote_curr not in fee_currencies:
        volume_api_buy_multiplier = API_BUY.get_best_bid_offer(market_quote_curr)
    elif market_quote_curr != API_BUY_fee_currency and market_quote_curr in fee_currencies:
        volume_api_buy_multiplier = get_value_in_user_currency(market_quote_curr, API_BUY_fee_currency, 1)
    if market_quote_curr != API_SELL_fee_currency and market_quote_curr not in fee_currencies:
        volume_api_sell_multiplier = API_SELL.get_best_bid_offer(market_quote_curr)
    elif market_quote_curr != API_SELL_fee_currency and market_quote_curr in fee_currencies:
        volume_api_sell_multiplier = get_value_in_user_currency(market_quote_curr, API_SELL_fee_currency, 1)

    for sell_offer in sell_offers:
        fees_buy = API_BUY.get_maker_taker_fee(user_volume_on_api1)
        volume_of_buy = float(sell_offer["quantity"]) * float(sell_offer["rate"])
        user_volume_on_api1 += (volume_of_buy * volume_api_buy_multiplier)
        cost_of_transaction = fees_buy["taker_fee"] * float(sell_offer["quantity"])
        deposited_crypto = float(sell_offer["quantity"]) - cost_of_transaction - API_BUY.get_withdrawal_list()[
            market_base_curr]
        remaining_money = deposited_crypto
        money_got_from_sell = 0
        for buy_offer in list(buy_offers):
            fees_sell = API_SELL.get_maker_taker_fee(user_volume_on_api2)
            volume_of_sell = float(buy_offer["quantity"]) * float(buy_offer["rate"])
            if remaining_money < float(buy_offer["quantity"]):
                volume_of_sell = remaining_money * float(buy_offer["rate"])
                cost_of_transaction = fees_sell["maker_fee"] * volume_of_sell
                user_volume_on_api2 += (volume_of_sell * volume_api_sell_multiplier)
                money_got_from_sell += (volume_of_sell - cost_of_transaction)
                break
            cost_of_transaction = fees_sell["taker_fee"] * volume_of_sell
            user_volume_on_api2 += (volume_of_sell * volume_api_sell_multiplier)
            money_got_from_sell += (volume_of_sell - cost_of_transaction)
            remaining_money -= float(buy_offer["quantity"])
            buy_offers.remove(buy_offer)
        money_earned_from_one_transaction = money_got_from_sell - volume_of_buy
        if money_earned_from_one_transaction > 0:
            earned_money += money_earned_from_one_transaction
        else:
            break
    return earned_money


def arbitrage_book(API1, user_volume_on_API1, API2, user_volume_on_API2):
    online_markets = find_online_markets(API1, API2)
    arbitrage_dictionary = dict()
    for market in online_markets:
        arbitrage_dictionary[market] = find_arbitrage(API1, user_volume_on_API1, API2, user_volume_on_API2, market)
    arbitrage_list = sorted(arbitrage_dictionary.items(), key=lambda market_arb: market_arb[1], reverse=True)
    return arbitrage_list
