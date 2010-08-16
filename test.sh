#!/bin/sh

#Because messing with paths tends to confuse coverage tests, copy the tests here
#so that the library is on the path
cp tests/test?*.py .

#run the tests
python-coverage -e
python-coverage -x testxstruct.py
python-coverage -x teststructures.py
python-coverage -x teststructureaccess.py
python-coverage -x testparser.py
python-coverage -x testpacking.py

#generate the html report
mkdir -p html
python-coverage -b -d html tp/netlib/xstruct.py tp/netlib/structures/*.py tp/netlib/parser.py

#get rid of the tests
rm *.py
