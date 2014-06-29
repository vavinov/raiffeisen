#!/usr/bin/env python

import sys
import locale
from decimal import *

def decimal(x):
    return Decimal(x.replace(",", ""))

CAR_LOAN = "776687 LOAN REPAY VAL"
CREDIT_CARD_ATM_TX_PREFIX = "Card ***7280 RBA ATM"
TCSBANK = "Fin.Inst. - Merchandise"

CR_CARD__GRACE_PERIOD = "CR. CARD GR PRD"
CR_CARD__OBLIGATORY = "CR. CARD OBLIG"
CR_CARD__INTEREST = "CR. CARD INTRST"
CR_CARD__PRINCIPAL = "CR. CARD PRNCPL"
CR_CARD__INSURANCE = "CR.CARD"

AUTO_CATS = [
    (lambda cat: is_supermarket_cat(cat), "Supermarket"),
    (lambda cat: is_cinema(cat), "Cinema"),
    (lambda cat: is_misc_cat(cat), "misc."),
    (lambda cat: is_clothes(cat), "Clothes & Shoes"),
    (lambda cat: cat == "Quick Payment Service", "Eating Places, Restaurants"),
]

def is_supermarket_cat(cat):
    return cat in [
        "Grocery Stores, Supermarkets", 
        "Misc.Food Stores,Special Mrkts", 
        "Department Stores"
    ]

def is_cinema(cat):
    return cat.startswith("Motion Picture Theatres") or cat.startswith("Theatr.") 

def is_misc_cat(cat):
    return cat.startswith("RC QW") or cat in [
        "Cash Advance Fee",
        "SMS Monthly Fee",
        "OVERLIMIT REPAYMENT",
        "Business Servs.not elsew.class",
        "News Dealers & newsstands",
        "Subscription Fee",
    ]

def is_clothes(cat):
    return cat.startswith("Misc.Apparel") or cat.startswith("Shoe Stores") or cat.startswith("Men's & Women's Clothing Store")

class AccountOperation:
    def __init__(self, fields):
        self.posting_date = fields[0]
        self.value_date = fields[1]
        if len(fields) == 6:
            self.tx_date = fields[2]
            ndi = 3
        else:
            self.tx_date = ''
            ndi = 2
        self.description = fields[ndi + 0].strip()
        self.tx_amount = fields[ndi + 1]
        self.delta = decimal(fields[ndi + 2])

    def prefix(self, prefix):
        return self.description.startswith(prefix)

    def is_credit_card_atm_tx(self):
        return self.prefix(CREDIT_CARD_ATM_TX_PREFIX)
    def is_card(self):
        return self.prefix("Card ***")
    def is_transfer(self):
        return self.prefix("P/O ")
    def is_credit_card_payment(self):
        return self.prefix(CR_CARD__INTEREST) or self.prefix(CR_CARD__PRINCIPAL) or self.prefix(CR_CARD__INSURANCE)
    def is_credit_card_misc(self):
        return self.prefix(CR_CARD__GRACE_PERIOD) or self.prefix(CR_CARD__OBLIGATORY)

    def is_regular(self):
        return self.is_credit_card_atm_tx() or (not self.is_card() and not self.is_transfer() and not self.is_credit_card_misc())
    def classifier(self):
        if self.prefix(CAR_LOAN):
            return "CAR LOAN"
        elif self.is_credit_card_payment():
            return "CR. CARD RPMN"
        elif is_misc_cat(self.description):
            return "misc."
        elif self.is_credit_card_atm_tx():
            return "ATM"
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

        for (predicate, name) in AUTO_CATS:
            if predicate(id):
                return name

        if id.startswith(TCSBANK):
            return "TCS bank"
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

if type_deltas.has_key('ATM') and type_deltas['ATM'] <= -38000:
    type_deltas['ATM'] += 34000
    type_deltas['Rent'] = -34000
    type_deltas['Car parking'] = -4000

def second(x):
    return x[1]

PRIORITY_CATS = set(["Rent", "Car parking", "CAR LOAN", "CR. CARD RPMN", "Service Stations"])

FORMAT="%-40s: %10.2f"
SUM_FORMAT="%-62s%10.2f"
def print_summary_priority(type_deltas):
    psum = print_summary(filter(lambda (k, v): k in PRIORITY_CATS, type_deltas))
    npsum = print_summary(filter(lambda (k, v): k not in PRIORITY_CATS, type_deltas))
    return psum + npsum

def print_summary(type_deltas):
    sum = 0
    for (k, v) in sorted(type_deltas, key=second):
        print FORMAT % (k, v)
        sum += v
    print SUM_FORMAT % ("", sum)
    return sum
   
income = print_summary([(ty, de) for (ty, de) in type_deltas.items() if de >= 0])
print
expense = print_summary_priority([(ty, de) for (ty, de) in type_deltas.items() if de < 0])
print
print SUM_FORMAT % ("", income + expense)
