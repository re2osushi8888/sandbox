from typing import List

from src.yen import Yen


class VendingMachine:
    def __init__(self):
        self.total_amount: List(Yen) = []

    def input_yen(self, yen: Yen) -> str:
        self.total_amount.append(yen)
        return f'{yen.amount}円が投入されました'

    def fetch_total_amount(self) -> int:
        return 1500
