#!/usr/bin/env bash
set -o errexit

# 1. Install dependencies
pip install -r requirements.txt

# 2. Compile Tailwind
# python manage.py tailwind install
cd theme/static_src
npm ci
cd ../..
python manage.py tailwind build

# 3. Collect static files
python manage.py collectstatic --no-input

# 4. Run migrations
python manage.py migrate
