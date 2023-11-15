from io import StringIO

import pytest

from src.controller import MoneyController


class TestMoneyController:
    def test_10円を投入できる(self, monkeypatch):
        mock_inputs = StringIO('10\n')
        monkeypatch.setattr('sys.stdin', mock_inputs)
        controller = MoneyController()
        money = controller.input()
        expected = "10円投入されました"
        assert expected == money

    def test_100円を投入できる(self, monkeypatch):
        mock_inputs = StringIO('100\n')
        monkeypatch.setattr('sys.stdin', mock_inputs)
        controller = MoneyController()
        money = controller.input()
        expected = "100円投入されました"
        assert expected == money

    def test_11円を投入したらValueError(self, monkeypatch):
        mock_inputs = StringIO('11\n')
        monkeypatch.setattr('sys.stdin', mock_inputs)
        controller = MoneyController()
        with pytest.raises(ValueError) as e:
            money = controller.input()
        expected = "硬貨・お札は1つずつ入れてください"
        assert str(e.value) == expected
