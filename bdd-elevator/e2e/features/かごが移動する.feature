Feature: かごが移動する

  Background:
    Given 最初のページにアクセスする
    And 階の表示が"1F"になっている

  Scenario: 人が2階でボタンを押す
    When "下"ボタンを押す
    Then 階の表示が"2F"と表示される
