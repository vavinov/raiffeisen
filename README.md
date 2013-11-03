
Downloading statements
----------------------

See connect.raiffeisen.ru menus (enable english interface!):

Credit cards:
 - Statement by Period:
   - save each month statement -> data/credit-account-statement-YYYYMMDD-YYYYMMDD.csv
   - it's a good idea to download these statements incrementally
 - Statement:
   - save whole period as a single statemnt -> data/credit-card-statement-YYYYMMDD-YYYYMMDD.csv

Debit cards:
 - Account statement:
   - save whole period as a single statemnt -> data/main-account-statement-YYYYMMDD-YYYYMMDD.csv
 - Statement
   - save whole period as a single statemnt -> data/main-card-statement-YYYYMMDD-YYYYMMDD.csv

Running analytics
-----------------

Use prepare.sh to prepare data.

Then run 
$ ./report.py combined-account-statement.csv  combined-card-statement.csv 10.2013

