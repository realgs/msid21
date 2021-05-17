from MarketConstants import *


class MarketFormatTransformer:

    @staticmethod
    def transform_market_format(market_name, data):
        if market_name == MARKET_BITTREX["name"]:
            return MarketFormatTransformer.__transform_bittrex_format(data)
        if market_name == MARKET_POLONIEX["name"]:
            return MarketFormatTransformer.__transform_poloniex_format(data)
        return None

    @staticmethod
    def __transform_bittrex_format(data):
        transformed_data_bids = [[] for _ in range(len(data))]
        transformed_data_asks = [[] for _ in range(len(data))]

        for i in range(len(data)):
            if not data[i]:
                data[i] = {"bid": [], "ask": []}
            elif "code" in data[i].keys():
                data[i]["bid"] = []
                data[i]["ask"] = []
                continue

            for j in range(len(data[i]["bid"])):
                data[i]["bid"][j] = (float(data[i]["bid"][j]["rate"]), float(data[i]["bid"][j]["quantity"]))
            for j in range(len(data[i]["ask"])):
                data[i]["ask"][j] = (float(data[i]["ask"][j]["rate"]), float(data[i]["ask"][j]["quantity"]))

        for i in range(len(data)):
            for j in range(len(data[i])):
                transformed_data_bids[i] = data[i]["bid"]

            for j in range(len(data[i])):
                transformed_data_asks[i] = data[i]["ask"]

        MarketFormatTransformer.__sort_data(transformed_data_bids, True)
        MarketFormatTransformer.__sort_data(transformed_data_asks, False)

        return transformed_data_bids, transformed_data_asks

    @staticmethod
    def __transform_poloniex_format(data):
        transformed_data_bids = [[] for _ in range(len(data))]
        transformed_data_asks = [[] for _ in range(len(data))]

        for i in range(len(data)):
            if not data[i]:
                data[i] = {"bids": [], "asks": []}
            elif "error" in data[i].keys():
                data[i]["bids"] = []
                data[i]["asks"] = []

            for j in range(len(data[i]["bids"])):
                data[i]["bids"][j] = (float(data[i]["bids"][j][0]), float(data[i]["bids"][j][1]))
            for j in range(len(data[i]["asks"])):
                data[i]["asks"][j] = (float(data[i]["asks"][j][0]), float(data[i]["asks"][j][1]))

        for i in range(len(data)):
            for j in range(len(data[i])):
                transformed_data_bids[i] = data[i]["bids"]

            for j in range(len(data[i])):
                transformed_data_asks[i] = data[i]["asks"]

        MarketFormatTransformer.__sort_data(transformed_data_bids, True)
        MarketFormatTransformer.__sort_data(transformed_data_asks, False)

        return transformed_data_bids, transformed_data_asks

    @staticmethod
    def __sort_data(data, rev):
        for i in range(len(data)):
            data[i].sort(key=lambda x: x[0], reverse=rev)
