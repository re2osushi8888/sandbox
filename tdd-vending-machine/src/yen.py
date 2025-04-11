
class Yen:
    allow_currency_value = [10, 50, 100, 500, 1000]

    def __init__(self, amount: int):
        if amount not in self.allow_currency_value:
            raise ValueError("通貨ではありません")
        self.amount = amount
