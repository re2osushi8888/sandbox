from src.yen import Yen


class TestYen:
    def test_金額に10を持つ円を作成できる(self):
        yen = Yen(10)
        assert yen.amount == 10
