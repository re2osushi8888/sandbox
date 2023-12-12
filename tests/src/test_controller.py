from io import StringIO

import pytest

from src.controller import CliController, MoneyController
from src.yen import Yen


class TestCliController:
    def test_標準入力で10と入力したらintの10で返って来る(self, monkeypatch):
        mock_inputs = StringIO('10\n')
        monkeypatch.setattr('sys.stdin', mock_inputs)

        controller = CliController()
        num = controller.input_str_to_int()
        assert num == 10

    def test_標準入力で100と入力したらintの100で返って来る(self, monkeypatch):
        mock_inputs = StringIO('100\n')
        monkeypatch.setattr('sys.stdin', mock_inputs)

        controller = CliController()
        num = controller.input_str_to_int()
        assert num == 100

    def test_abcdeと文字列が入力されたときValueError(self):
        controller = CliController()
        string = 'abcde'
        with pytest.raises(ValueError) as e:
            controller.convert_string_to_int(string)
        assert str(e.value) == "数値で入力してください"


class TestMoneyController:
    def test_10と入力したら10円が返ってくる(self, monkeypatch):
        mock_inputs = StringIO('10\n')
        monkeypatch.setattr('sys.stdin', mock_inputs)
        controller = MoneyController()
        money: Yen = controller.input()
        assert Yen(10).amount == money.amount

    def test_100と入力したら100円が返返ってくる(self, monkeypatch):
        mock_inputs = StringIO('100\n')
        monkeypatch.setattr('sys.stdin', mock_inputs)
        controller = MoneyController()
        money: Yen = controller.input()
        assert Yen(100).amount == money.amount

    def test_11と入力したらValueError(self, monkeypatch):
        mock_inputs = StringIO('11\n')
        monkeypatch.setattr('sys.stdin', mock_inputs)
        controller = MoneyController()
        with pytest.raises(ValueError) as e:
            controller.input()
        expected = "硬貨・お札は1つずつ入れてください"
        assert str(e.value) == expected

