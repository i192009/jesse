from jesse import utils
from jesse.strategies import Strategy
import jesse.helpers as jh


class TestWalletBalance(Strategy):
    def before(self):
        if self.index == 0:
            assert self.position.exchange.wallet_balance == 10000 == self.balance
            assert self.position.exchange.available_margin == 10000 == self.available_margin
            assert self.leveraged_available_margin == 20000

        if self.price == 11:
            # wallet balance should have stayed the same while we haven't spent from it yet
            assert self.position.exchange.wallet_balance == 10000 == self.balance
            # Adjusted available_margin calculation
            assert round(self.position.exchange.available_margin) == 10000 - (4000 / 2) == round(self.available_margin)
            assert round(self.leveraged_available_margin) == 20000 - 4000

        if self.price == 12:
            # wallet balance should have changed because of fees, but we have fee=0 in this test, so:
            assert self.position.exchange.wallet_balance == 10000 == self.balance
            # Adjusted available_margin calculation
            assert round(self.position.exchange.available_margin) == 10000 - (4000 / 2) == round(self.available_margin)

        if self.price == 21:
            # wallet balance must now equal to 10_000 + the profit we made from previous trade
            previous_trade = self.trades[0]
            assert self.position.exchange.wallet_balance == previous_trade.pnl + 10000
            # now that position is closed, available_margin should equal to wallet_balance
            assert self.position.exchange.available_margin == previous_trade.pnl + 10000 == self.available_margin
            assert self.balance == self.position.exchange.wallet_balance
            assert self.balance == self.available_margin

    def should_long(self) -> bool:
        return self.price == 10

    def should_short(self) -> bool:
        return False

    def go_long(self):
        qty1 = utils.size_to_qty(2000, self.price + 2)
        qty2 = utils.size_to_qty(2000, self.price + 4)
        self.buy = [
            (qty1, self.price + 2),
            (qty2, self.price + 4),
        ]

    def update_position(self):
        if self.price == 20:
            self.liquidate()

    def go_short(self):
        pass

    def should_cancel_entry(self):
        return False
