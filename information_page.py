from tkinter import *
import constants
import constants_alphavantage
import gui
import alphavantage
import bitbay
import binance
import helpers


class InformationPage(Frame):
    resources = []

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.configure(background=constants.BACKGROUND)

        self.bit = bitbay.Bitbay(0.0043)
        self.bin = binance.Binance(0.001)

        l_percent = Label(self, text="How many %:", bg=constants.HEADER_BG, fg=constants.HEADER_FG,
                           font=constants.HEADER_FONT)
        l_percent.place(x=5, y=220)

        self.e_percent = Entry(self, width=constants.ENTRY_WIDTH)
        self.e_percent.configure(font=constants.ENTRY_FONT)
        self.e_percent.place(x=150, y=220)

        b_show = Button(self, text='Show', bg=constants.BUTTON_BG, fg=constants.BUTTON_FG,
                         font=constants.BUTTON_FONT, width=constants.BUTTON_WIDTH,
                         command=lambda: self.show())
        b_show.place(x=100, y=255)

        b_back = Button(self, text='Back', bg=constants.BUTTON_BG, fg=constants.BUTTON_FG, font=constants.BUTTON_FONT,
                        width=constants.BUTTON_WIDTH,
                        command=lambda: controller.show_frame('StartPage'))
        b_back.place(x=100, y=325)

    def get_resources(self):
        result = []
        for i in gui.wallet.resources[constants.STOCKS]:
            result.append((constants.STOCKS, i))
        for i in gui.wallet.resources[constants.CURRENCIES]:
            result.append((constants.CURRENCIES, i))
        for i in gui.wallet.resources[constants.CRYPTOCURRENCIES]:
            result.append((constants.CRYPTOCURRENCIES, i))
        return result

    def show(self):
        percent = self.e_percent.get()
        resources = self.get_resources()
        wl = gui.wallet.resources
        base = wl[constants.BASE_CURRENCY]
        columns = ['Name', 'Quantity', 'Price', 'Value', 'Netto', percent+'%', 'Netto', 'Recommended', 'Arbitrage']

        for c in range(len(columns)):
            Label(self, text=columns[c], background=constants.TABLE_BACKGROUND, foreground=constants.TABLE_FOREGROUND,borderwidth=constants.BORDER_WIDTH).grid(row=0, column=c)

        for r in range(len(resources)):
            arb = '-'
            resource = resources[r]
            type = resource[0]
            name = resource[1]
            qu = wl[type][name][constants.QUANTITY]
            pr = wl[type][name][constants.PRICE]
            cost = qu*pr
            cost_part = qu*pr*float(percent)/100
            Label(self, text=name, background=constants.TABLE_BACKGROUND, foreground=constants.TABLE_FOREGROUND, borderwidth=constants.BORDER_WIDTH).grid(row=r + 1, column=0)
            Label(self, text=qu, background=constants.TABLE_BACKGROUND, foreground=constants.TABLE_FOREGROUND, borderwidth=constants.BORDER_WIDTH).grid(row=r + 1,
                                                                                                          column=1)
            Label(self, text=pr, background=constants.TABLE_BACKGROUND, foreground=constants.TABLE_FOREGROUND, borderwidth=constants.BORDER_WIDTH).grid(row=r + 1,
                                                                                                       column=2)
            rate = helpers.value_in_base(base, 1)
            if type == constants.STOCKS:
                price = alphavantage.get_stock_price(name)
                rec = '-'
                if price[constants.STATUS] == constants_alphavantage.OK and rate[constants.STATUS] == constants.OK:
                    value = round(rate[constants.VALUE] * price[constants_alphavantage.PRICE] * qu, 2)
                    value_part = round(value * float(percent)/100, 2)
                    tax = 0 if cost > value else 0.19 * (value - cost)
                    netto = round(value - tax, 2)
                    netto_part = round(netto*float(percent)/100, 2)
                else:
                    value = '-'
                    value_part = '-'
                    netto = '-'
                    netto_part = '-'

            elif type == constants.CURRENCIES and rate[constants.STATUS] == constants.OK:
                price = alphavantage.get_offer(name, base)
                if price[constants.STATUS] == constants_alphavantage.OK:
                    value = round(rate[constants.VALUE] * price[constants.BID] * qu, 2)
                    value_part = round(value * float(percent) / 100, 2)
                    tax=0 if cost > value else 0.19 * (value - cost)
                    netto = round(value - tax, 2)
                    netto_part = round(netto * float(percent) / 100, 2)
                    rec = 'FOR'
                else:
                    value = '-'
                    value_part = '-'
                    netto = '-'
                    netto_part = '-'
                    rec = '-'

            elif type == constants.CRYPTOCURRENCIES and rate[constants.STATUS] == constants.OK:
                price = helpers.valuation(self.bit, name, qu)
                price_bin = helpers.valuation(self.bin, name, qu)
                price_part = helpers.valuation(self.bit, name, qu * float(percent)/100)
                if price[constants.STATUS] == constants.OK:
                    if price_bin[constants.STATUS] == constants.OK:
                        rec = 'BIN' if price_bin[constants.V_VALUE] > price[constants.V_VALUE] else 'BIT'
                    else:
                        rec = '-'
                    value = round(rate[constants.VALUE] * price[constants.V_VALUE], 2)
                    value_part = round(rate[constants.VALUE] * price_part[constants.V_VALUE], 2)
                    tax = 0 if cost > value else 0.19 * (value - cost)
                    tax_part = 0 if cost_part > value_part else 0.19 * (value_part - cost_part)
                    netto = round(value - tax, 2)
                    netto_part = round(value_part - tax_part, 2)

                    for crypto in wl[constants.CRYPTOCURRENCIES]:
                        earn = helpers.calc_arbitrage(self.bit, self.bin, (crypto, name))[constants.CA_EARNINGS]
                        if not earn == None and earn > 0:
                            arb = 'BIT-BIN, ' + crypto + '-' + name

                    for crypto in wl[constants.CRYPTOCURRENCIES]:
                        earn = helpers.calc_arbitrage(self.bin, self.bit, (crypto, name))[constants.CA_EARNINGS]
                        if not earn == None and earn > 0:
                            arb = 'BIN-BIT, ' + crypto + '-' + name

                else:
                    value = '-'
                    value_part = '-'
                    netto = '-'
                    netto_part = '-'
                    rec = '-'
            Label(self, text=value, background=constants.TABLE_BACKGROUND, foreground=constants.TABLE_FOREGROUND,
                    borderwidth=constants.BORDER_WIDTH).grid(row=r + 1, column=3)
            Label(self, text=netto, background=constants.TABLE_BACKGROUND, foreground=constants.TABLE_FOREGROUND,
                    borderwidth=constants.BORDER_WIDTH).grid(row=r + 1, column=4)
            Label(self, text=value_part, background=constants.TABLE_BACKGROUND,
                    foreground=constants.TABLE_FOREGROUND,
                    borderwidth=constants.BORDER_WIDTH).grid(row=r + 1, column=5)
            Label(self, text=netto_part, background=constants.TABLE_BACKGROUND,
                    foreground=constants.TABLE_FOREGROUND,
                    borderwidth=constants.BORDER_WIDTH).grid(row=r + 1, column=6)
            Label(self, text=rec, background=constants.TABLE_BACKGROUND,
                  foreground=constants.TABLE_FOREGROUND,
                  borderwidth=constants.BORDER_WIDTH).grid(row=r + 1, column=7)
            Label(self, text=arb, background=constants.TABLE_BACKGROUND,
                  foreground=constants.TABLE_FOREGROUND,
                  borderwidth=constants.BORDER_WIDTH).grid(row=r + 1, column=8)
