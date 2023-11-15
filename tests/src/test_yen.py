import pytest

from src.yen import Yen


class TestYen:
    def test_金額に10を持つ円を作成できる(self):
        yen = Yen(10)
        assert yen.amount == 10

    def test_金額に100を持つ円を作成できる(self):
        yen = Yen(100)
        assert yen.amount == 100

    def test_11円の場合ValueError(self):
        with pytest.raises(ValueError) as e:
            Yen(11)
        assert str(e.value) == "通貨ではありません"
