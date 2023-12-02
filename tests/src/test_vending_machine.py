from src.vending_machine import VendingMachine
from src.yen import Yen


class TestVendingMachine:
    def test_10円を投入するとmoney_listに保存されている(self):
        machine = VendingMachine()
        yen = Yen(10)
        machine.input_yen(yen)
        excpected = [yen]
        assert machine.money_list == excpected

    def test_500円と100円を投入するとmoney_listに保存されている(self):
        machine = VendingMachine()
        yen_1 = Yen(500)
        yen_2 = Yen(100)
        machine.input_yen(yen_1)
        machine.input_yen(yen_2)
        excpected = [yen_1, yen_2]
        assert machine.money_list == excpected

    def test_500円と1000円を投入し投入金額の総計をintで取得できる(self):
        machine = VendingMachine()
        machine.input_yen(Yen(500))
        machine.input_yen(Yen(1000))
        total_amount: int = machine.fetch_total_amount()
        excpected = 1500
        assert total_amount == excpected

    def test_100円と10円を投入し投入金額の総計をintで取得できる(self):
        machine = VendingMachine()
        machine.input_yen(Yen(100))
        machine.input_yen(Yen(10))
        total_amount: int = machine.fetch_total_amount()
        excpected = 110
        assert total_amount == excpected



    # def test_通貨にない数字を入力すると投入やり直し():

    # def test_お金の投入を複数回できる():

    # def test_払い戻し操作を行うと投入金額の総計を釣銭として出力する():
