from src.yen import Yen


class VendingMachine:
    def input_yen(self, yen: Yen) -> str:
        return f'{yen.amount}円が投入されました'
