#!/usr/bin/env python

import sys
import locale
from decimal import *

def decimal(x):
    return Decimal(x.replace(",", ""))

CAR_LOAN = "776687 LOAN REPAY VAL"

def is_supermarket_cat(cat):
    return cat in [
        "Grocery Stores, Supermarkets", 
        "Misc.Food Stores,Special Mrkts", 
        "Department Stores"
    ]

def is_misc_cat(cat):
    return cat.startswith("RC QW") or cat in [
        "Cash Advance Fee",
        "Quick Payment Service",
        "SMS Monthly Fee",
        "OVERLIMIT REPAYMENT"
    ]

class AccountOperation:
    def __init__(self, fields):
        self.posting_date = fields[0]
        self.value_date = fields[1]
        self.tx_date = fields[2]
        self.description = fields[3].strip()
        self.tx_amount = fields[4]
        self.delta = decimal(fields[5])
    def is_card(self):
        return self.description.startswith("Card ***")
    def is_transfer(self):
        return self.description.startswith("P/O ")
    def is_obligatory_repayment(self):
        return self.description == "CR. CARD OBLIG RPMN"

    def is_regular(self):
        return not self.is_card() and not self.is_transfer() #and not self.is_obligatory_repayment()
    def classifier(self):
        if self.description.startswith(CAR_LOAN):
            return CAR_LOAN
        elif self.description.startswith("CR. CARD") or self.description.startswith("CR.CARD"):
            return "CR. CARD RPMN"
        elif is_misc_cat(self.description):
            return "misc."
        else:
            return self.description
    def get_delta(self):
        return self.delta
    def get_date(self):
        return self.tx_date if len(self.tx_date) > 0 else self.value_date

class CardOperation:
    def __init__(self, fields):
        self.tx_date = fields[0]
        self.value_date = fields[1]
        self.currency = fields[2]
        self.description = fields[3].strip()
        self.merchant_type = fields[4].strip()
        self.city = fields[5]
        self.country = fields[6]
        self.delta = decimal(fields[7])
        self.tx_amount = fields[8]
    def is_card(self):
        return self.description.startswith("Card ***")

    def is_regular(self):
        return not self.is_card()

    def classifier(self):
        if len(self.merchant_type) == 0:
            id = self.description
        else:
            id = self.merchant_type

        if is_supermarket_cat(id):
            return "Supermarket"
        elif is_misc_cat(id):
            return "misc."
        else:
            return id

    def get_delta(self):
        return self.delta
    def get_date(self):
        return self.tx_date

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

account_statement_file = sys.argv[1]
card_statement_file = sys.argv[2]
month_year = sys.argv[3]

with open(account_statement_file, "r") as f:
    account_operations = [AccountOperation(l.strip().split(";")) for l in f]

with open(card_statement_file, "r") as f:
    card_operations = [CardOperation(l.strip().split(";")) for l in f]

type_deltas = {}
for o in account_operations + card_operations:
    if o.get_date().endswith(month_year):
        if o.is_regular():
            t = o.classifier()
            type_deltas[t] = type_deltas.get(t, 0) + o.get_delta()
        else:
            #print "ignoring", o.__dict__
            pass

def second(x):
    return x[1]

FORMAT="%-40s: %10.2f"
SUM_FORMAT="%-62s%10.2f"
def print_summary(type_deltas):
    sum = 0
    for (k, v) in sorted(type_deltas, key=second):
        print FORMAT % (k, v)
        sum += v
    print SUM_FORMAT % ("", sum)
    return sum
   
income = print_summary((ty, de) for (ty, de) in type_deltas.items() if de >= 0)
print
expense = print_summary((ty, de) for (ty, de) in type_deltas.items() if de < 0)
print
print SUM_FORMAT % ("", income + expense)
