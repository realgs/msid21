from finance import showTransactionsForCurrencies, showPriceDifferenceStream

myCurrencies = [("BTC", "USD"), ("ETH", "PLN"), ("ZEC", "USD")]
count = 10
interval = 5

# prints to console last <count> transactions for each currency
showTransactionsForCurrencies(myCurrencies, count)

# prints to console difference between sell price and buy price in percent with default interval
showPriceDifferenceStream(myCurrencies, interval)
