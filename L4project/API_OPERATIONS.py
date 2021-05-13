import BITBAY
import BITTREX
import NBP

bitbay = BITBAY.Bitbay()
bittrex = BITTREX.Bittrex()


def find_online_markets(API1, API2):
    API1_markets = API1.request_market_data()
    API2_markets = API2.request_market_data()
    API1_markets_length = len(API1_markets)
    API2_markets_length = len(API2_markets)
    API_with_less_markets = API1_markets
    API_with_more_markets = API2_markets
    online_markets = []

    if API2_markets_length < API1_markets_length:
        API_with_less_markets = API2_markets
        API_with_more_markets = API1_markets

    for market in API_with_less_markets:
        if market in API_with_more_markets:
            online_markets.append(market)

    return online_markets

def get_value_in_user_currency(init_currency: str, target_currency: str, money: float):
    target_currency_value_of_money = money
    if init_currency != "PLN":
        money_in_PLN = NBP.exchange_rate_average(init_currency) * money
        target_currency_value_of_money = money_in_PLN
    if target_currency != "PLN":
        money_in_target_currency = money/NBP.exchange_rate_average(target_currency)
        target_currency_value_of_money = money_in_target_currency
    return target_currency_value_of_money

# print(find_online_markets(bitbay,bittrex))

def sell_currency_on_api(init_val_user_amount_of_currency: float, currency: str,
                         init_val_user_overall_volume_on_api: float, user_default_currency: str, API_to_sell_on):
    user_volume_on_api = init_val_user_overall_volume_on_api
    user_amount_of_currency = init_val_user_amount_of_currency
    user_money_earned = 0
    market = (currency, API_to_sell_on.get_upper_bound_currency())
    bids_asks_data = API_to_sell_on.request_bids_and_asks(market)
    bids = bids_asks_data["bid"].sort(key=lambda bid: bid["rate"], reverse=True)

    for bid in bids:
        fees = API_to_sell_on.get_maker_taker_fee(user_volume_on_api)
        volume_of_transaction = bid["quantity"] * bid["rate"]
        if user_amount_of_currency < bid["quantity"]:
            volume_of_transaction = user_amount_of_currency * bid["rate"]
            cost_of_transaction = fees["maker_fee"] * volume_of_transaction
            user_volume_on_api += volume_of_transaction
            user_money_earned += (volume_of_transaction - cost_of_transaction)
            user_amount_of_currency = 0
            break
        cost_of_transaction = fees["taker_fee"] * volume_of_transaction
        user_volume_on_api += volume_of_transaction
        user_money_earned += (volume_of_transaction - cost_of_transaction)
        user_amount_of_currency -= bid["quantity"]

    earned_money = user_money_earned
    if API_to_sell_on.get_upper_bound_currency() != user_default_currency:
        earned_money = get_value_in_user_currency(API_to_sell_on.get_upper_bound_currency, user_default_currency, user_money_earned)
    return earned_money