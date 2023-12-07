from src.yen import Yen


class CliController:
    def input_str_to_int(self):
        input_str = input()
        return int(input_str)


class MoneyController:
    def input(self):
        money_amount = input('お金を投入してください')
        if money_amount not in ['10', '50', '100', '500', '1000']:
            raise ValueError('硬貨・お札は1つずつ入れてください')
        money = Yen(int(money_amount))
        return money
