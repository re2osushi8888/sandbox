from typing import List

from src.controller import CliController
from src.yen import Yen


class VendingMachine:
    def __init__(self):
        # TODO: money_listはファーストクラスコレクション化する
        self.money_list: List(Yen) = []
        self.controller = CliController()

    def input_yen(self, yen: Yen):
        self.money_list.append(yen)

    def fetch_total_amount(self) -> int:
        total_amount = 0
        for money in self.money_list:
            total_amount += money.amount
        return total_amount

    def refund(self):
        """呼び出された時点の合計値を返し、money_listを空にする"""
        total_amount = self.fetch_total_amount()
        self.money_list = []
        return total_amount

    def select_action(self, action_number: int):
        if action_number == 1:
            amount = self.controller.input_str_to_int()
            self.input_yen(Yen(amount))
        if action_number == 2:
            total_amount = self.fetch_total_amount()
            print(f'総計は{total_amount}円です')
        if action_number == 3:
            charge = self.refund()
            print(f'おつりの総計は{charge}円です')

    def start(self):
        # TODO: テストどうすればいいのか矢田さん聞く
        print('起動します')
        while True:
            print('\n1: お金を投入')
            print('2: 投入金額の確認')
            print('3: 払い戻し')
            action_number = input(':')
            self.select_action(int(action_number))
            print('#######################')
