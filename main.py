import random
import sqlite3


class BankAccount:
    number = ""
    pin = ""
    balance = 0

    def __init__(self, number=None, pin=None):
        self.number = number
        self.pin = pin


class BankingSystemDatabase:
    database_connection = None

    def __init__(self):
        self.database_connection = sqlite3.connect('card.s3db')
        cur = self.database_connection.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS card('
                    'id INTEGER DEFAULT 0, '
                    'number TEXT, '
                    'pin TEXT, '
                    'balance INTEGER DEFAULT 0)')

    def get_bank_account_by_number(self, number):
        cur = self.database_connection.cursor()
        cur.execute('SELECT * FROM card WHERE number = ?', [number])
        result = cur.fetchone()
        if result is None:
            return None
        bank_account = BankAccount()
        bank_account.number = result[1]
        bank_account.pin = result[2]
        bank_account.balance = result[3]
        return bank_account

    def insert_bank_account(self, new_bank_account):
        cur = self.database_connection.cursor()
        params = (new_bank_account.number, new_bank_account.pin)
        cur.execute('INSERT INTO card (number, pin) VALUES (?,?)', params)
        self.database_connection.commit()

    def update_bank_account(self, bank_account):
        cur = self.database_connection.cursor()
        params = (bank_account.number, bank_account.pin, bank_account.balance, bank_account.number)
        cur.execute('UPDATE card SET number = ?, pin = ?, balance = ? WHERE number = ?', params)
        self.database_connection.commit()

    def close_bank_account(self, cc_number):
        cur = self.database_connection.cursor()
        cur.execute('DELETE FROM card WHERE number = ?', [cc_number])
        self.database_connection.commit()


    def __del__(self):
        self.database_connection.close()


class BankingSystem:
    bank_accounts = {}
    banking_system_database = None

    def __init__(self):
        self.banking_system_database = BankingSystemDatabase()

    def create_account(self):
        number = self.__generate_card_number()

        pin = "".join(["{}".format(random.randint(0, 9)) for num in range(0, 4)])
        new_bank_account = BankAccount(number, pin)
        self.banking_system_database.insert_bank_account(new_bank_account)
        return new_bank_account

    def __generate_card_number(self):
        cc_number = "400000" + "".join(["{}".format(random.randint(0, 9)) for num in range(0, 9)])
        multiply_odd_digits = []
        index = 1
        for digit in cc_number:
            if index % 2 == 1:
                multiply_odd_digits.append(2 * int(digit))
                index += 1

            elif index % 2 == 0:
                multiply_odd_digits.append(int(digit))
                index += 1
        index = 0
        for number in multiply_odd_digits:
            if number >= 10:
                multiply_odd_digits[index] = number - 9
            index += 1

        for number in range(0, 10):
            if (sum(multiply_odd_digits) + number) % 10 == 0:
                cc_number = cc_number + str(number)

        return cc_number

    def check_luhn_number(self, cc_number):
        multiply_odd_digits = []
        index = 0

        for digit in cc_number:
            if index % 2 == 0:
                multiply_odd_digits.append(2 * int(digit))
                index += 1

            elif index % 2 == 1:
                multiply_odd_digits.append(int(digit))
                index += 1
            if index == 16:
                break

        index = 0
        total = 0

        for number in multiply_odd_digits:
            if number >= 10:
                multiply_odd_digits[index] = number - 9
            total += multiply_odd_digits[index]
            index += 1

        if total % 10 != 0:
            return False

        else:
            return True

    def log_into_account(self, cc_number, pin_number):
        bank_account = self.banking_system_database.get_bank_account_by_number(cc_number)

        if bank_account is None:
            return None

        if pin_number != bank_account.pin:
            return None

        return bank_account

    def add_income(self, deposit, cc_number):
        current_bank_account = self.banking_system_database.get_bank_account_by_number(cc_number)
        current_bank_account.balance = current_bank_account.balance + deposit
        self.banking_system_database.update_bank_account(current_bank_account)

    def deduct_income(self, deposit, cc_number):
        current_bank_account = self.banking_system_database.get_bank_account_by_number(cc_number)
        current_bank_account.balance = current_bank_account.balance - deposit
        self.banking_system_database.update_bank_account(current_bank_account)

    def check_bank_account(self, recipient_bank_account_number):
        if self.banking_system_database.get_bank_account_by_number(recipient_bank_account_number) is None:
            return False
        return True

    def do_transfer(self, transfer_amount, recipient_bank_account_number, sender_bank_account_number):
        if self.banking_system_database.get_bank_account_by_number(sender_bank_account_number).balance < transfer_amount:
            return False
        self.add_income(transfer_amount, recipient_bank_account_number)
        self.deduct_income(transfer_amount, sender_bank_account_number)
        return True

    def close_bank_account(self, cc_number):
        self.banking_system_database.close_bank_account(cc_number)


banking_system = BankingSystem()

while True:
    action = input("1. Create an account\n2. Log into account\n0. Exit\n")

    if action == "1":
        new_bank_account = banking_system.create_account()
        print("\nYour card number:\n{}".format(new_bank_account.number))
        print("Your card PIN:\n{}\n".format(new_bank_account.pin))
        continue

    if action == "2":
        credit_card_number = input("Enter your card number:")
        pin_number = input("Enter your PIN:")

        if banking_system.log_into_account(credit_card_number, pin_number) is not None:
            print("\nYou have successfully logged in!")
            while True:
                action_inside = input(
                    "\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n")
                if action_inside == "1":
                    print(banking_system.log_into_account(credit_card_number, pin_number).balance)
                if action_inside == "2":
                    deposit = int(input('Enter income:'))
                    banking_system.add_income(deposit, credit_card_number)
                    print("Income was added!")
                if action_inside == "3":
                    recipient_bank_account = input("Enter card number:")
                    if recipient_bank_account == credit_card_number:
                        print("You can't transfer money to the same account!")
                        continue

                    if not banking_system.check_luhn_number(recipient_bank_account):
                        print("Probably you made a mistake in the card number. Please try again!")
                        continue

                    if not banking_system.check_bank_account(recipient_bank_account):
                        print("Such a card does not exist.")
                        continue

                    transfer_amount = int(input("Enter how much money you want to transfer:"))

                    if not banking_system.do_transfer(transfer_amount, recipient_bank_account, credit_card_number):
                        print("Not enough money!")

                if action_inside == "4":
                    banking_system.close_bank_account(credit_card_number)
                    print("The account has been closed!")


                if action_inside == "5":
                    print("You have successfully logged out!")
                    break
                if action_inside == "0":
                    print("Bye!")
                    exit()

        else:
            print("Wrong card number or PIN!")
            continue

    if action == "0":
        print("Bye!")
        break
