#!/usr/bin/env bash
set -euo pipefail

python manage.py migrate --noinput
python manage.py create_default_superuser
python manage.py collectstatic --noinput
