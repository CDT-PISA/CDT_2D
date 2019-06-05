#!/bin/bash

rm cdt_2d

cd ../../build
make install

cd ..
mv bin/cdt_2d test/out/cdt_2d

# launch the test
# cdt_2d is called with: RUN_NUM LAMBDA G_YM TIMELENGTH END_CONDITION DEBUG_FLAG LAST_CHKPT LINEAR_HISTORY
cd test/out

rm -f iterations_done runs.txt
rm -rf history
mkdir history

RUN_NUM=1
LAMBDA=0.7
G_YM=1.
TIMELENGTH=10
END_CONDITION=10s
DEBUG_FLAG=false
LAST_CHKPT=None
LINEAR_HISTORY=0
./cdt_2d $RUN_NUM $LAMBDA $G_YM $TIMELENGTH $END_CONDITION $DEBUG_FLAG $LAST_CHKPT $LINEAR_HISTORY
