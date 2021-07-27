#!/bin/bash

echo CONVERTING srk_data
paste - - - - - - - - - - - - - < srk_data.txt > srk_data.csv

echo COPYING .fld FILE
cp ../TREND\ 4.0/srk/fluids_srk/srkfluids.fld ./srkfluids.fld
