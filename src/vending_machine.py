from typing import List

from src.yen import Yen


class VendingMachine:
    def __init__(self):
        self.money_list: List(Yen) = []

    def input_yen(self, yen: Yen):
        self.money_list.append(yen)

    def fetch_total_amount(self) -> int:
        total_amount = 0
        for money in self.money_list:
            total_amount += money.amount
        return total_amount
