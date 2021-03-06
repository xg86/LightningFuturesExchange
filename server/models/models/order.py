from shared.shared import db
from enum import Enum
import datetime
import copy
from equity import Equity
import math

class OrderType(Enum):
    MARKET = 0
    LIMIT = 1
    TRIGGER = 2
    TRAILING_STOP = 3
    RANGE = 4
    MARGIN_CALL = 5
    INTEREST_PAYMENT = 6
    EXCHANGE_FEE = 7


class OrderStatus(Enum):
    OPENED = 0
    CLOSED = 1
    CLOSED_MARGIN = 2


class Order(db.Model):
    equity_id = db.Column(db.Integer, primary_key=True, nullable=False)
    order_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    is_margin_call = db.Column(db.Boolean, nullable=False)
    prev_order_id = db.Column(db.BigInteger, nullable=False)
    next_order_id = db.Column(db.BigInteger, nullable=False)
    modification_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    is_long = db.Column(db.Boolean, nullable=False)
    quantity = db.Column(db.BigInteger, nullable=False)
    order_type = db.Column(db.Integer, nullable=False)
    price = db.Column(db.BigInteger, nullable=False)
    has_trigger_limit = db.Column(db.Boolean, nullable=False)
    trigger_price = db.Column(db.BigInteger, nullable=False)
    trigger_limit_price = db.Column(db.BigInteger, nullable=False)
    has_trailing_limit = db.Column(db.Boolean, nullable=False)
    trailing_start_transaction_id = db.Column(db.BigInteger, nullable=False)
    trailing_stop_percent = db.Column(db.Integer, nullable=False)
    trailing_stop_limit_percent = db.Column(db.Integer, nullable=False)
    filled_quantity = db.Column(db.BigInteger, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    created_date = db.Column(db.DateTime(), nullable=False)
    closed_date = db.Column(db.DateTime())

    def __init__(self):
        self.effective_price = 0
        self.trailing_price_max = -1
        self.trailing_price = -1
        self.trailing_price_limit = -1

    def __init(self, dic):
        self.effective_price = 0
        self.trailing_price_max = -1
        self.trailing_price = -1
        self.trailing_price_limit = -1
        self.from_dic(dic)

    @staticmethod
    def new_market_order(equity_id, order_id, user_id, is_long, quantity):
        order = Order()
        order.equity_id = equity_id
        order.order_id = order_id
        order.is_margin_call = False
        order.user_id = user_id
        order.prev_order_id = -1
        order.next_order_id = -1
        order.modification_id = order_id
        order.is_long = is_long
        order.order_type = OrderType.MARKET
        order.price = -1
        order.has_trigger_limit = False
        order.trigger_price = 0
        order.trigger_limit_price = 0
        order.has_trailing_limit = False
        order.trailing_start_transaction_id = 0
        order.trailing_stop_percent = 0
        order.trailing_stop_limit_percent = 0
        order.filled_quantity = 0
        order.status = OrderStatus.OPENED
        order.created_date = datetime.datetime.utcnow()
        order.closed_date = None
        return order

    def clone(self):
        return copy.copy(self)

    def copy_values(self, item):
        self.__dict__.update(item.__dict__)

    def close(self):
        self.status = OrderStatus.CLOSED
        self.closed_date = datetime.datetime.utcnow()

    def is_filled(self):
        return self.filled_quantity == self.quantity

    def get_price(self):
        return self.effective_price

    def get_long_short_string(self):
        return "long" if self.is_long else "short"

    def get_quantity(self, equity):
        return self.quantity * math.pow(10, equity.decimal_points_quantity)

    def remaining_quantity(self, equity):
        return (self.quantity - self.filled_quantity) * math.pow(10, equity.decimal_points_quantity)

    def update_trailing_price(self):
        self.trailing_price = ((10000.0 + ((1 if self.is_long else -1) * self.trailing_stop_percent)) / 10000.0)
        self.effective_price = self.trailing_price

    @staticmethod
    def price_comparer(item1, item2):
        comp = -1 if item1.price > item2.price else 1 if item1.price < item2.price else 0
        if comp != 0:
            return comp

        return -1 if item1.order_id > item2.order_id else 1 if item1.order_id < item2.order_id else 0

    @staticmethod
    def price_comparer_dec(item1, item2):
        comp = 1 if item1.price > item2.price else -1 if item1.price < item2.price else 0
        if comp != 0:
            return comp

        return -1 if item1.order_id > item2.order_id else 1 if item1.order_id < item2.order_id else 0

    @staticmethod
    def trigger_price_comparer(item1, item2):
        comp = -1 if item1.trigger_price > item2.trigger_price else 1 if item1.trigger_price < item2.trigger_price else 0
        if comp != 0:
            return comp

        return -1 if item1.order_id > item2.order_id else 1 if item1.order_id < item2.order_id else 0

    @staticmethod
    def trigger_price_comparer_dec(item1, item2):
        comp = 1 if item1.trigger_price > item2.trigger_price else -1 if item1.trigger_price < item2.trigger_price else 0
        if comp != 0:
            return comp

        return -1 if item1.order_id > item2.order_id else 1 if item1.order_id < item2.order_id else 0

    @staticmethod
    def trailing_price_comparer(item1, item2):
        comp = -1 if item1.trailing_price > item2.trailing_price else 1 if item1.trailing_price < item2.trailing_price else 0
        if comp != 0:
            return comp

        return -1 if item1.order_id > item2.order_id else 1 if item1.order_id < item2.order_id else 0

    @staticmethod
    def trailing_price_comparer_dec(item1, item2):
        comp = 1 if item1.trailing_price > item2.trailing_price else -1 if item1.trailing_price < item2.trailing_price else 0
        if comp != 0:
            return comp

        return -1 if item1.order_id > item2.order_id else 1 if item1.order_id < item2.order_id else 0

    @staticmethod
    def trailing_price_max_comparer(item1, item2):
        comp = -1 if item1.trailing_price_max > item2.trailing_price_max else 1 if item1.trailing_price_max < item2.trailing_price_max else 0
        if comp != 0:
            return comp

        return -1 if item1.order_id > item2.order_id else 1 if item1.order_id < item2.order_id else 0

    @staticmethod
    def trailing_price_max_comparer_dec(item1, item2):
        comp = 1 if item1.trailing_price_max > item2.trailing_price_max else -1 if item1.trailing_price_max < item2.trailing_price_max else 0
        if comp != 0:
            return comp

        return -1 if item1.order_id > item2.order_id else 1 if item1.order_id < item2.order_id else 0

    @staticmethod
    def effective_price_comparer(item1, item2):
        comp = -1 if item1.effective_price > item2.effective_price else 1 if item1.effective_price < item2.effective_price else 0
        if comp != 0:
            return comp

        return -1 if item1.order_id > item2.order_id else 1 if item1.order_id < item2.order_id else 0

    @staticmethod
    def effective_price_comparer_dec(item1, item2):
        comp = 1 if item1.effective_price > item2.effective_price else -1 if item1.effective_price < item2.effective_price else 0
        if comp != 0:
            return comp

        return -1 if item1.order_id > item2.order_id else 1 if item1.order_id < item2.order_id else 0

    @staticmethod
    def id_comparer(item1, item2):
        return 1 if item1.order_id < item2.order_id else -1 if item1.order_id > item2.order_id else 0

    @staticmethod
    def modification_id_comparer(item1, item2):
        return 1 if item1.modification_id < item2.modification_id else -1 if item1.modification_id > item2.modification_id else 0

    @staticmethod
    def is_opened_long_limit(item):
        return item.is_opened() and item.is_limit() and item.is_long

    @staticmethod
    def is_opened_short_limit(item):
        return item.is_opened() and item.is_limit() and not item.is_long

    @staticmethod
    def is_opened_long_trigger(item):
        return item.is_opened() and item.is_trigger() and item.is_long

    @staticmethod
    def is_opened_short_trigger(item):
        return item.is_opened() and item.is_trigger() and not item.is_long

    @staticmethod
    def is_opened_long_trailing(item):
        return item.is_opened() and item.is_trailing() and item.is_long

    @staticmethod
    def is_opened_short_trailing(item):
        return item.is_opened() and item.is_trailing() and not item.is_long

    def should_trigger_execute(self, equity):
        if self.is_long:
            return equity.price >= self.trigger_price
        else:
            return equity.price <= self.trigger_price

    def execute_trigger(self):
        self.price = self.trigger_limit_price
        self.order_type = OrderType.MARKET if self.price < 0 else OrderType.LIMIT

    def set_trailing_price(self, equity):
        self.trailing_price_max = equity.current_price

        tsp = self.trailing_stop_percent if self.is_long else -self.trailing_stop_percent
        pm = Equity.PERCENT_MULTIPLIER

        float_price = ((pm + tsp) / (pm + 0.0)) * equity.current_price

        if self.is_long:
            self.trailing_price = math.floor(float_price)
        else:
            self.trailing_price = math.ceil(float_price)

        self.trailing_price = ((pm + tsp) / (pm + 0.0)) * equity.current_price

        if self.has_trailing_limit:
            tslp = self.trailing_stop_limit_percent if self.is_long else -self.trailing_stop_limit_percent

            pm = Equity.PERCENT_MULTIPLIER

            float_price = ((pm + tslp) / (pm + 0.0)) * equity.current_price

            if self.is_long:
                self.trailing_price_limit = math.ceil(float_price)
            else:
                self.trailing_price_limit = math.floor(float_price)

        self.calculate_effective_price()

    def close_and_create_triggered_order(self, next_id, current_price):
        self.close()
        self.next_order_id = next_id

        order_type = OrderType.LIMIT
        price = -1

        has_trigger_limit = False
        trigger_price = 0
        trigger_limit_price = 0
        activation_price = 0

        if self.order_type == OrderType.TRIGGER or (self.order_type == OrderType.RANGE and self.price < 0):
            if self.has_trigger_limit:
                price = self.trigger_limit_price
            else:
                price = -1
                order_type = OrderType.MARKET

            activation_price = self.trigger_price

        elif self.order_type == OrderType.TRAILING_STOP:
            if self.has_trailing_limit:
                price = self.trailing_price_limit
            else:
                price = -1
                order_type = OrderType.MARKET

            activation_price = self.trailing_price

        elif self.order_type == OrderType.RANGE:
            if self.is_long and self.trigger_price >= current_price or not self.is_long and self.trigger_price <= current_price:
                if self.has_trigger_limit:
                    price = self.trigger_limit_price
                else:
                    price = -1
                    order_type = OrderType.MARKET

                activation_price = self.trigger_price
            else:
                if self.has_trailing_limit:
                    price = self.trailing_price_limit
                    order_type = OrderType.Range

                    has_trigger_limit = self.has_trigger_limit
                    trigger_price = self.trigger_price
                    trigger_limit_price = self.trigger_limit_price
                else:
                    price = -1
                    order_type = OrderType.MARKET

                activation_price = self.trailing_price

        order = Order(
            equity_id=self.equity_id,
            order_id=next_id,
            user_id=self.user_id,
            is_margin_call=False,
            prev_order_id=self.order_id,
            next_order_id=-1,
            modification_id=next_id,
            is_long=self.is_long,
            quantity=self.quantity,
            order_type=order_type,
            price=price,
            has_trigger_limit=has_trigger_limit,
            trigger_price=trigger_price,
            trigger_limit_price=trigger_limit_price,
            has_trailing_limit=False,
            trailing_start_transaction_id=-1,
            trailing_stop_percent=0,
            trailing_stop_limit_percent=0,
            filled_quantity=0,
            status=OrderStatus.OPENED,
            created_date=datetime.datetime.utcnow(),
            closed_date=None
        )

        order.trailing_price = activation_price

        order.calculate_effective_price()

        return order

    def is_opened(self):
        return self.order_status == OrderStatus.OPENED

    def is_limit(self):
        if self.order_type == OrderType.LIMIT:
            return True
        elif self.order_type == OrderType.MARKET:
            return True
        elif self.order_type == OrderType.RANGE and self.price >= 0:
            return True
        return False

    def is_trigger(self):
        if self.order_type == OrderType.TRIGGER or self.order_type == OrderType.RANGE:
            return True

    def is_only_trigger(self):
        return self.order_type == OrderType.TRIGGER

    def is_trailing(self):
        if self.order_type == OrderType.TRAILING_STOP:
            return True
        elif self.order_type == OrderType.RANGE and self.price == -1:
            return True
        return False

    def is_only_trailing(self):
        return self.order_type == OrderType.TRAILING_STOP

    def get_order_type_string(self):
        if self.order_type == OrderType.MARKET:
            return "market_order"
        elif self.order_type == OrderType.LIMIT:
            return "limit_order"
        elif self.order_type == OrderType.TRIGGER:
            return "trigger_order"
        elif self.order_type == OrderType.TRAILING_STOP:
            return "trailing_order"
        elif self.order_type == OrderType.RANGE:
            return "range_order"

    def intersects(self, order):
        if self.is_long == order.is_long:
            return False

        if not self.is_limit_or_market() and not order.is_limit_or_market():
            return False

        if self.price < 0 or order.price < 0:
            return True

        if order.is_long:
            return order.price >= self.price
        else:
            return order.price <= self.price

    def is_limit_or_market(self):
        return self.order_type == OrderType.LIMIT or self.order_type == OrderType.MARKET

    def calculate_effective_price(self):
        if self.order_type == OrderType.LIMIT:
            self.effective_price = self.price
        elif self.order_type == OrderType.TRIGGER:
            self.effective_price = self.trigger_price
        elif self.order_type == OrderType.TRAILING_STOP:
            self.effective_price = self.trailing_price
        elif self.order_type == OrderType.RANGE:
            self.effective_price = max(self.trailing_price, self.trigger_price, self.price)

    def to_dic(self):
        return {
            "equityId": self.equity_id,
            "userId": self.user_id,
            "orderId": self.order_id,
            "prev_order_id": self.prev_order_id,
            "next_order_id": self.prev_order_id,
            "isMarginCall": self.is_margin_call,
            "isLong": self.is_long,
            "quantity": self.quantity,
            "orderType": self.order_type,
            "price": self.price,
            "hasTriggerLimit": self.has_trigger_limit,
            "triggerPrice": self.trigger_price,
            "triggerLimitPrice": self.trigger_limit_price,
            "hasTrailingLimit": self.has_trailing_limit,
            "trailingStopPercent": self.trailing_stop_percent,
            "trailingStopLimitPercent": self.trailing_stop_limit_percent,
            "filledQuantity": self.filled_quantity,
            "status": self.status,
            "createdDate": self.created_date,
            "closedDate": self.closed_date
        }

    def to_dic_private(self):
        return {
            "equityId": self.equity_id,
            "orderId": self.order_id,
            "isLong": self.is_long,
            "isMarginCall": self.is_margin_call,
            "quantity": self.quantity,
            "orderType": self.order_type,
            "price": self.price,
            "hasTriggerLimit": self.has_trigger_limit,
            "triggerPrice": self.trigger_price,
            "triggerLimitPrice": self.trigger_limit_price,
            "hasTrailingLimit": self.has_trailing_limit,
            "trailingStopPercent": self.trailing_stop_percent,
            "trailingStopLimitPercent": self.trailing_stop_limit_percent,
            "filledQuantity": self.filled_quantity,
            "status": self.status,
            "createdDate": self.created_date,
            "closedDate": self.closed_date,
            "is_deleted": self.is_deleted,
            "modification_id": self.modification_id
        }

    def from_dic(self, dic):
        self.equity_id = int(dic.get("equityId", -1))
        self.user_id = int(dic.get("userId", -1))
        self.order_id = None
        self.prev_order_id = -1
        self.next_order_id = -1
        self.is_margin_call = dic.get("isMarginCall", False)
        self.is_long = dic.get("isLong", True)
        self.quantity = int(dic.get("quantity", -1))
        self.order_type = int(dic.get("orderType", -1))
        self.price = int(dic.get("price", -1))
        self.has_trigger_limit = dic.get("hasTriggerLimit", False)
        self.trigger_price = int(dic.get("triggerPrice", -1))
        self.trigger_limit_price = int(dic.get("triggerLimitPrice", -1))
        self.has_trailing_limit = dic.get("hasTrailingLimit", False),
        self.trailing_stop_percent = int(dic.get("trailingStopPercent", -1))
        self.trailing_stop_limit_percent = int(dic.get("trailingStopLimitPercent", -1))
        self.filled_quantity = 0
        self.status = OrderStatus.OPENED
        self.created_date = datetime.datetime.utcnow()
        self.closed_date = None

    def is_valid(self):
        if self.equity_id < 0:
            return False

        if self.user_id < 0:
            return False

        if not isinstance(self.is_long, bool):
            return False

        if self.quantity < 0:
            return False

        if self.order_type < 0 or self.order_type > 4:
            return False

        if self.order_type == OrderType.MARKET:
            self.price = 0
            self.has_trailing_limit = False
            self.trigger_price = 0
            self.trigger_limit_price = 0
            self.has_trailing_limit = False
            self.trailing_stop_percent = 0
            self.trailing_stop_limit_percent = 0
        elif self.order_type == OrderType.LIMIT:
            self.has_trailing_limit = False
            self.trigger_price = 0
            self.trigger_limit_price = 0
            self.has_trailing_limit = False
            self.trailing_stop_percent = 0
            self.trailing_stop_limit_percent = 0
        elif self.order_type == OrderType.TRIGGER:
            self.price = 0
            self.has_trailing_limit = False
            self.trailing_stop_percent = 0
            self.trailing_stop_limit_percent = 0
            if self.has_trigger_limit:
                if self.is_long:
                    if self.trigger_price > self.trigger_limit_price:
                        return False
                else:
                    if self.trigger_price < self.trigger_limit_price:
                        return False
            else:
                self.trigger_limit_price = 0
        elif self.order_type == OrderType.TRAILING_STOP:
            self.price = 0
            self.has_trigger_limit = False
            self.trigger_price = 0
            self.trigger_limit_price = 0

            if not self.has_trailing_limit:
                self.trailing_stop_limit_percent = 0

            if 100 > self.trailing_stop_percent or self.trailing_stop_percent > 10000:
                return False

            if self.has_trailing_limit:
                if 0 > self.trailing_stop_limit_percent or self.trailing_stop_limit_percent > 10000:
                    return False
        elif self.order_type == OrderType.RANGE:
            if self.price == 0:
                if not self.has_trailing_limit:
                    self.trailing_stop_limit_percent = 0

                if 100 > self.trailing_stop_percent or self.trailing_stop_percent > 10000:
                    return False

                if self.has_trailing_limit:
                    if 0 > self.trailing_stop_limit_percent or self.trailing_stop_limit_percent > 10000:
                        return False
            else:
                self.has_trailing_limit = False
                self.trailing_stop_percent = 0
                self.trailing_stop_limit_percent = 0
                if self.is_long:
                    if self.price > self.trigger_price:
                        return False
                else:
                    if self.price < self.trigger_price:
                        return False

            if self.has_trigger_limit:
                if self.is_long:
                    if self.trigger_price > self.trigger_limit_price:
                        return False
                else:
                    if self.trigger_price < self.trigger_limit_price:
                        return False
            else:
                self.trigger_limit_price = 0

        if self.price < 0:
            return False

        if not isinstance(self.has_trigger_limit, bool):
            return False

        if self.trigger_price < 0:
            return False

        if self.trigger_limit_price < 0:
            return False

        if not isinstance(self.has_trailing_limit, bool):
            return False

        if self.trailing_stop_percent < 0:
            return False

        if self.trailing_stop_limit_percent < 0:
            return False


db.Index('ix_order_user_id_equity_id', Order.user_id, Order.equity_id, Order.order_id)
