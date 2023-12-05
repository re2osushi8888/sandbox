from typing import List

from src.controller import MoneyController
from src.yen import Yen


class VendingMachine:
    def __init__(self):
        # TODO: money_listはファーストクラスコレクション化する
        self.money_list: List(Yen) = []
        self.controller: MoneyController = MoneyController()

    def input_yen(self, yen: Yen):
        self.money_list.append(yen)

    def fetch_total_amount(self) -> int:
        total_amount = 0
        for money in self.money_list:
            total_amount += money.amount
        return total_amount

    def refund(self):
        total_amount = self.fetch_total_amount()
        self.money_list = []
        print(f'{total_amount}円')

    def select_action(self, action_number: int):
        if action_number == 1:
            yen = self.controller.input()
            self.input_yen(yen)
        if action_number == 2:
            total_amount = self.fetch_total_amount()
            print(f'総計は{total_amount}円です')
