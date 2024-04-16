#! /bin/bash

if [[ ! $(which pip) =~ "roles_royce" ]]; then
  echo "make sure you run with venv activated"
  exit 1
fi

rm -rf requirements.txt
pip3 install -e .
pip3 freeze -l | grep -v '-e git' > requirements.txt
