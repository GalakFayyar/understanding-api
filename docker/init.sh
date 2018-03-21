#!/bin/bash
set -e

echo "Starting SSH ..."
service ssh start

# service supervisor start

# service supervisor status

python /code/api.py