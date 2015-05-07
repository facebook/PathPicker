#!/bin/bash
PEPLINES=$(autopep8 --recursive ./src/ --diff | wc -l)
if (( PEPLINES > 0 )); then
  echo "Not Pep8 compliant:";
  autopep8 --recursive ./src/ --diff
  exit 1;
fi

python ./src/test.py > /dev/null
if [ $? -eq 0 ]
then
  echo "Tests passed!"
else
  echo "Tests failed :*("
  exit 1
fi

