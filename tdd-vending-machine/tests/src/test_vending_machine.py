import sys
from io import StringIO

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
        excpected = 110
        assert machine.fetch_total_amount() == excpected

    def test_1000円と500円を投入し払い戻し操作で総計1500を返す(self):
        machine = VendingMachine()
        machine.input_yen(Yen(1000))
        machine.input_yen(Yen(500))

        change = machine.refund()
        assert change == 1500

    def test_10円と100円を投入し払い戻し操作で総計110を返す(self):
        machine = VendingMachine()
        machine.input_yen(Yen(10))
        machine.input_yen(Yen(100))

        charge = machine.refund()
        assert charge == 110

    def test_100円と100円を投入し払い戻し操作でmoney_listが空になり総計200が返ってくる(self):
        machine = VendingMachine()
        yen_1 = Yen(100)
        yen_2 = Yen(100)
        machine.input_yen(yen_1)
        machine.input_yen(yen_2)
        expected = [yen_1, yen_2]
        assert machine.money_list == expected

        charge = machine.refund()
        assert charge == 200
        assert machine.money_list == []

    def test_行動選択で1を入力しCLIで100を入力して100円を投入できる(self, monkeypatch):
        mock_inputs = StringIO('100\n')
        monkeypatch.setattr('sys.stdin', mock_inputs)

        machine = VendingMachine()
        action_number = 1
        machine.select_action(action_number)
        assert machine.fetch_total_amount() == 100

    def test_行動選択で2を入力しお金の総計が出力される(self):
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            machine = VendingMachine()
            machine.input_yen(Yen(100))

            action_number = 2
            machine.select_action(action_number)

            captured_output.seek(0)
            output = captured_output.read().strip()
            excpected = '総計は100円です'
            assert output == excpected
            # 自動販売機にお金が残っていることを確認
            assert machine.fetch_total_amount() == 100
        finally:
            sys.stdout = sys.__stdout__

    def test_行動選択で3を入力しお金が払い戻され総計が出力される(self):
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            machine = VendingMachine()
            machine.input_yen(Yen(1000))
            machine.input_yen(Yen(500))
            # 自動販売機にお金があることを確認
            assert machine.fetch_total_amount() == 1500

            action_number = 3
            machine.select_action(action_number)

            captured_output.seek(0)
            output = captured_output.read().strip()
            excpected = 'おつりの総計は1500円です'
            assert output == excpected
            # 自動販売機にお金がないことを確認
            assert machine.fetch_total_amount() == 0
        finally:
            sys.stdout = sys.__stdout__

    # def test_通貨にない数字を入力すると投入やり直し():

    # def test_お金の投入を複数回できる():

    # def test_払い戻し操作を行うと投入金額の総計を釣銭として出力する():
