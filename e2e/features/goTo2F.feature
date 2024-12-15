Feature: 人が2階で下ボタンを押すと、階の表示が2になっている

  Background:
    Given かごが1階にある

  Scenario: 人が2階でボタンを押す
    When "下"ボタンを押す
    Then "2F"と表示される

