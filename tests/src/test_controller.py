from io import StringIO

from src.controller import MoneyController


class TestMoneyController:
    def test_10円を投入できる(self, monkeypatch):
        mock_inputs = StringIO('10\n')
        monkeypatch.setattr('sys.stdin', mock_inputs)
        controller = MoneyController()
        money = controller.input()
        expected = "10円投入されました"
        assert expected == money
