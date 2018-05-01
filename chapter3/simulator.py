# -*- coding: utf-8 -*-
import collections
import pandas as pd
import japandas
import math

def calc_tax(total_profit):
    """儲けに対する税金計算
    """
    if total_profit < 0:
        return 0
    return int(total_profit * 0.20315)


def calc_fee(total):
    """約定手数料計算(楽天証券の場合）
    """
    if total <= 50000:
        return 54
    elif total <= 100000:
        return 97
    elif total <= 200000:
        return 113
    elif total <= 500000:
        return 270
    elif total <= 1000000:
        return 525
    elif total <= 1500000:
        return 628
    elif total <= 30000000:
        return 994
    else:
        return 1050


def calc_cost_of_buying(count, price):
    """株を買うのに必要なコストと手数料を計算
    """
    subtotal = int(count * price)
    fee = calc_fee(subtotal)
    return subtotal + fee, fee


def calc_cost_of_selling(count, price):
    """株を売るのに必要なコストと手数料を計算
    """
    subtotal = int(count * price)
    fee = calc_fee(subtotal)
    return fee, fee


class OwnedStock(object):
    def __init__(self):
        self.total_cost = 0    # 取得にかかったコスト（総額)
        self.total_count = 0   # 取得した株数(総数)
        self.current_count = 0 # 現在保有している株数
        self.average_cost = 0  # 平均取得価額

    def append(self, count, cost):
        if self.total_count != self.current_count:
            self.total_count = self.current_count
            self.total_cost = self.current_count * self.average_cost
        self.total_cost += cost
        self.total_count += count
        self.current_count += count
        self.average_cost = math.ceil(self.total_cost / self.total_count)

    def remove(self, count):
        if self.current_count < count:
            raise ValueError("can't remove", self.total_cost, count)
        self.current_count -= count

class Portfolio(object):

    def __init__(self, deposit):
        self.deposit = deposit  # 現在の預り金
        self.amount_of_investment = deposit  # 投資総額
        self.total_profit = 0  # 総利益（税引き前）
        self.total_tax = 0  # （源泉徴収)税金合計
        self.total_fee = 0  # 手数料合計
        self.stocks = collections.defaultdict(OwnedStock)  # 保有銘柄 銘柄コード　-> OwnedStock への辞書

    def add_deposit(self, deposit):
        """預り金を増やす (= 証券会社に入金)
        """
        self.deposit += deposit
        self.amount_of_investment += deposit

    def buy_stock(self, code, count, price):
        """株を買う
        """
        cost, fee = calc_cost_of_buying(count, price)
        if cost > self.deposit:
            raise ValueError('cost > deposit', cost, self.deposit)

        # 保有株数増加
        self.stocks[code].append(count, cost)

        self.deposit -= cost
        self.total_fee += fee

    def sell_stock(self, code, count, price):
        """株を売る
        """
        subtotal = int(count * price)
        cost, fee = calc_cost_of_selling(count, price)
        if cost > self.deposit + subtotal:
            raise ValueError('cost > deposit + subtotal',
                             cost, self.deposit + subtotal)

        # 保有株数減算
        stock = self.stocks[code]
        average_cost = stock.average_cost
        stock.remove(count)
        if stock.current_count == 0:
            del self.stocks[code]

        # 儲け計算
        profit = int((price - average_cost) * count - cost)
        self.total_profit += profit

        # 源泉徴収額決定
        current_tax = calc_tax(self.total_profit)
        withholding = current_tax - self.total_tax
        self.total_tax = current_tax

        self.deposit += subtotal - cost - withholding
        self.total_fee += fee

    def calc_current_total_price(self, get_current_price_func):
        """現在の評価額を返す
        """
        stock_price = sum(get_current_price_func(code)
                          * stock.current_count
                          for code, stock in self.stocks.items())
        return stock_price + self.deposit




class Order(object):

    def __init__(self, code):
        self.code = code

    def execute(self, date, portfolio, get_price_func):
        pass

    @classmethod
    def default_order_logger(cls, order_type, date, code, count, price, before_deposit, after_deposit):
        print("{} {} code:{} count:{} price:{} deposit:{} -> {}".format(
            date.strftime('%Y-%m-%d'),
            order_type,
            code,
            count,
            price,
            before_deposit,
            after_deposit
        ))
    logger = default_order_logger

class BuyMarketOrderAsPossible(Order):
    """残高で買えるだけ買う成行注文
    """

    def __init__(self, code, unit):
        super().__init__(code)
        self.unit = unit

    def execute(self, date, portfolio, get_price_func):
        price = get_price_func(self.code)
        count_of_buying_unit = int(portfolio.deposit / price / self.unit)
        while count_of_buying_unit:
            try:
                count = count_of_buying_unit * self.unit
                prev_deposit = portfolio.deposit
                portfolio.buy_stock(self.code, count, price)
                self.logger("BUY", date, self.code, count, price, prev_deposit, portfolio.deposit)
            except ValueError:
                count_of_buying_unit -= 1
            else:
                break


class BuyMarketOrderMoreThan(Order):
    """指定額以上で最小の株数を買う
    """
    def __init__(self, code, unit, under_limit):
        super().__init__(code)
        self.unit = unit
        self.under_limit = under_limit

    def execute(self, date, portfolio, get_price_func):
        price = get_price_func(self.code)
        unit_price = price * self.unit
        if unit_price > self.under_limit:
            count_of_buying_unit = 1
        else:
            count_of_buying_unit = int(self.under_limit / unit_price)
        while count_of_buying_unit:
            try:
                count = count_of_buying_unit * self.unit
                prev_deposit = portfolio.deposit
                portfolio.buy_stock(self.code, count, price)
                self.logger("BUY", date, self.code, count, price, prev_deposit, portfolio.deposit)
            except ValueError:
                count_of_buying_unit -= 1
            else:
                break

class SellMarketOrder(Order):
    """成行の売り注文
    """
    def __init__(self, code, count):
        super().__init__(code)
        self.count = count

    def execute(self, date, portfolio, get_price_func):
        price = get_price_func(self.code)
        prev_deposit = portfolio.deposit
        portfolio.sell_stock(self.code, self.count, price)
        self.logger("SELL", date, self.code, self.count, price, prev_deposit, portfolio.deposit)

def tse_date_range(start_date, end_date):
    tse_business_day = pd.offsets.CustomBusinessDay(
        calendar=japandas.TSEHolidayCalendar())
    return pd.date_range(start_date, end_date,
                         freq=tse_business_day)

def simulate(start_date, end_date, deposit, trade_func,
             get_open_price_func, get_close_price_func):
    """
    [start_date, end_date]の範囲内の売買シミュレーションを行う
    deposit: 最初の所持金
    trade_func:
        シミュレーションする取引関数
        （引数 date, portfolio でOrderのリストを返す関数）
    get_open_price_func:
        指定銘柄コードの指定日の始値を返す関数 (引数 date, code)
    get_close_price_func:
        指定銘柄コードの指定日の始値を返す関数 (引数 date, code)
    """

    portfolio = Portfolio(deposit)

    total_price_list = []
    profit_or_loss_list = []
    def record(d):
        # 本日(d)の損益などを記録
        current_total_price = portfolio.calc_current_total_price(
            lambda code: get_close_price_func(d, code))
        total_price_list.append(current_total_price)
        profit_or_loss_list.append(current_total_price
                                   - portfolio.amount_of_investment)

    def execute_order(d, orders):
        # 本日(d)において注文(orders)をすべて執行する
        for order in orders:
            order.execute(date, portfolio,
                          lambda code: get_open_price_func(d, code))

    order_list = []
    date_range = [pdate.to_pydatetime().date()
                  for pdate in tse_date_range(start_date, end_date)]
    for date in date_range[:-1]:
        execute_order(date, order_list)          # 前日に行われた注文を執行
        order_list = trade_func(date, portfolio) # 明日実行する注文を決定する
        record(date)                             # 損益等の記録

    # 最終日に保有株は全部売却
    last_date = date_range[-1]
    execute_order(last_date,
                  [SellMarketOrder(code, stock.current_count)
                   for code, stock in portfolio.stocks.items()])
    record(last_date)

    return portfolio, \
           pd.DataFrame(data={'price': total_price_list,
                              'profit': profit_or_loss_list},
                        index=date_range)
