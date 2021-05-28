from APIs.API import API


class CryptoAPI(API):
    def get_fees(self, price, amount, crypto_currency):
        if crypto_currency in self.TRANSFER_FEE:
            return price * amount * self.TAKER_FEE + self.TRANSFER_FEE[crypto_currency]
        else:
            raise Exception("Transfer fee not mapped for " + crypto_currency)

    def calculate_arbitrage(self, other_market, crypto_currency, base_currency, buyOrSellOnBitBay):
        if buyOrSellOnBitBay == "sell":  # buy here sell there
            buy_market = self
            sell_market = other_market
        else:
            buy_market = other_market
            sell_market = self

        sell_offers_order_book = buy_market.get_orderbook_sorted(crypto_currency, base_currency, "sell") # i can buy this
        buy_offers_order_book = sell_market.get_orderbook_sorted(crypto_currency, base_currency, "buy") # and sell it here

        best_sell_offer = float(sell_offers_order_book[0][buy_market.RATE]) # cheapest on top
        best_sell_offer_amount = float(sell_offers_order_book[0][buy_market.QUANTITY])
        best_buy_offer = float(buy_offers_order_book[len(buy_offers_order_book)-1][sell_market.RATE]) # on top someone wants to pay the most
        best_buy_offer_amount = float(buy_offers_order_book[len(buy_offers_order_book)-1][sell_market.QUANTITY])

        if best_buy_offer_amount < best_sell_offer_amount:  # if someone wants to buy less than i have to sell
            fees_for_buying = buy_market.get_fees(best_sell_offer, best_sell_offer_amount, crypto_currency)
            fees_for_selling = sell_market.get_fees(best_buy_offer, best_buy_offer_amount, crypto_currency)
            return best_buy_offer * best_buy_offer_amount - best_sell_offer * best_buy_offer_amount - fees_for_buying - fees_for_selling
        else:
            missing_amount = best_buy_offer_amount
            total = 0
            i = len(buy_offers_order_book) - 1

            while missing_amount >= 0 and i < len(sell_offers_order_book):
                fees_for_buying = buy_market.get_fees(best_sell_offer, best_sell_offer_amount, crypto_currency)
                fees_for_selling = sell_market.get_fees(best_buy_offer, best_buy_offer_amount, crypto_currency)
                total = total + best_buy_offer * best_buy_offer_amount - best_sell_offer * best_buy_offer_amount - fees_for_buying - fees_for_selling
                missing_amount = missing_amount - best_sell_offer_amount
                i = i - 1
                best_sell_offer = float(sell_offers_order_book[i][buy_market.RATE])
                best_sell_offer_amount = float(sell_offers_order_book[i][buy_market.QUANTITY])

        return total

    def quick_sort_orderbook_by_rate(self, unsorted):
        if len(unsorted) <= 1:
            return unsorted

        pivot = unsorted.pop()

        lower = []
        greater = []

        for item in unsorted:
            if float(item.get(self.RATE)) < float(pivot.get(self.RATE)):
                lower.append(item)
            else:
                greater.append(item)

        return self.quick_sort_orderbook_by_rate(lower) + [pivot] + self.quick_sort_orderbook_by_rate(greater)
