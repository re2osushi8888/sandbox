from src.vending_machine import VendingMachine
from src.yen import Yen


class TestVendingMachine:
    def test_10円を投入できる(self):
        machine = VendingMachine()
        message = machine.input_yen(Yen(10))
        assert message == '10円が投入されました'

    # def test_通貨にない数字を入力すると投入やり直し():

    # def test_お金の投入を複数回できる():

    # def test_投入金額の総計を取得できる():

    # def test_払い戻し操作を行うと投入金額の総計を釣銭として出力する():
