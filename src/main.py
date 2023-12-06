import os
import sys

sys.path.append(os.getcwd())
from src.vending_machine import VendingMachine  # NOQA


def main():
    machine = VendingMachine()
    machine.start()


if __name__ == "__main__":
    main()
