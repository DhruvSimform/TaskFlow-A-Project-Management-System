#!/bin/sh

echo "Database ready! Running migrations..."
uv run manage.py migrate

echo "Creating superuser..."
# Set default values if not passed as environment variables
SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-admin@gmail.com}
SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD:-admin}
SUPERUSER_FIRST_NAME=${DJANGO_SUPERUSER_FIRST_NAME:-Admin}
SUPERUSER_LAST_NAME=${DJANGO_SUPERUSER_LAST_NAME:-User}
SUPERUSER_ROLE=${DJANGO_SUPERUSER_ROLE:-ADMIN}

echo "Creating Django superuser..."

uv run manage.py shell <<EOF
from django.contrib.auth import get_user_model

User = get_user_model()
email = "${SUPERUSER_EMAIL}"

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email="${SUPERUSER_EMAIL}",
        password="${SUPERUSER_PASSWORD}",
        first_name="${SUPERUSER_FIRST_NAME}",
        last_name="${SUPERUSER_LAST_NAME}",
        role="${SUPERUSER_ROLE}"
    )
    print("Superuser created successfully.")
else:
    print("Superuser with email '\${SUPERUSER_EMAIL}' already exists.")
EOF

echo "Starting server..."
exec "$@"
