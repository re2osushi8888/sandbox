

class MoneyController:
    def input(self):
        money = input('お金を投入してください')
        if money not in ['10', '50', '100', '500', '1000']:
            raise ValueError('硬貨・お札は1つずつ入れてください')
        return f'{money}円投入されました'
