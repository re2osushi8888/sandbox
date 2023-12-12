from src.yen import Yen


class CliController:
    def input_str_to_int(self):
        "標準入力を受け付ける。数字以外はvalueErrorを返す"
        input_str = input()
        return self.convert_string_to_int(input_str)

    def convert_string_to_int(self, input_string: str):
        try:
            num = int(input_string)
            return num
        except ValueError:
            raise ValueError('数値で入力してください')


class MoneyController:
    def input(self):
        money_amount = input('お金を投入してください')
        if money_amount not in ['10', '50', '100', '500', '1000']:
            raise ValueError('硬貨・お札は1つずつ入れてください')
        money = Yen(int(money_amount))
        return money
