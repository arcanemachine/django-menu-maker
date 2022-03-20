#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

echo "PROJECT_NAME_PYTHON is set to: '$PROJECT_NAME_PYTHON'"
echo "PROJECT_PORT_INTERNAL is set to: '$PROJECT_PORT_INTERNAL'"

/app/init.sh
python3 manage.py collectstatic --noinput
python3 manage.py makemigrations
python3 manage.py migrate

exec "$@"
