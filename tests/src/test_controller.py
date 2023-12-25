from io import StringIO

import pytest

from src.controller import CliController


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

    def test_abcdeと文字列が入力されたときValueError(self, monkeypatch):
        mock_inputs = StringIO('abcde\n')
        monkeypatch.setattr('sys.stdin', mock_inputs)

        controller = CliController()
        with pytest.raises(ValueError) as e:
            controller.input_str_to_int()
        assert str(e.value) == "数値で入力してください"

    def test_メッセージ入力するとinput関数の引数に入る(self, monkeypatch):
        # memo: chatgptに聞いたけど微妙かも..
        def mock_input(message):
            assert message == "数字を入力してください："
            return 10

        monkeypatch.setattr('builtins.input', mock_input)

        controller = CliController()
        message = '数字を入力してください：'
        user_input = controller.input_str_to_int(message)

        assert user_input == 10
