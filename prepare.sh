#!/bin/sh
cat data/*card-statement* | iconv -f windows-1251 >combined-card-statement.csv
cat data/*account-statement* | iconv -f windows-1251 >combined-account-statement.csv
