from src.yen import Yen


class MoneyController:
    def input(self):
        money_amount = input('お金を投入してください')
        if money_amount not in ['10', '50', '100', '500', '1000']:
            raise ValueError('硬貨・お札は1つずつ入れてください')
        money = Yen(int(money_amount))
        return money
