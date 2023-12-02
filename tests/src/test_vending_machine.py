from src.vending_machine import VendingMachine
from src.yen import Yen


class TestVendingMachine:
    def test_10円を投入できる(self):
        machine = VendingMachine()
        message = machine.input_yen(Yen(10))
        assert message == '10円が投入されました'

    def test_100円を投入できる(self):
        machine = VendingMachine()
        message = machine.input_yen(Yen(100))
        assert message == '100円が投入されました'

    def test_500円と1000円を投入し投入金額の総計を取得できる():
        machine = VendingMachine()
        machine.input_yen(Yen(500))
        machine.input_yen(Yen(1000))
        total_amount: Yen = machine.fetch_total_amount()
        excpected = Yen(1500)
        assert total_amount.amount == excpected.amount


    # def test_通貨にない数字を入力すると投入やり直し():

    # def test_お金の投入を複数回できる():

    # def test_払い戻し操作を行うと投入金額の総計を釣銭として出力する():
