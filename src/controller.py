class CliController:
    def input_str_to_int(self, message: str = None) -> int:
        """標準入力を受け付ける。数字以外はvalueErrorを返す

        Args:
            message (str, optional): メッセージを出力する

        Raises:
            ValueError: 数値以外が入力されたとき

        Returns:
            int: 入力値をintで返却
        """
        input_str = input(message)
        try:
            int_num = int(input_str)
        except ValueError:
            raise ValueError('数値で入力してください')
        return int_num
