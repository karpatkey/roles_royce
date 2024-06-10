#! /bin/bash

if [[ ! $(which pip) =~ "roles_royce" ]]; then
  echo "make sure you run with venv activated"
  exit 1
fi

pip3 uninstall -y -r <(pip freeze)
pip3 install -r requirements-apps.txt
pip3 install -e ../../.
pip3 freeze -l | grep -v '-e git' > requirements.txt
pip3 install -r ../../requirements-dev.txt
