#!/usr/bin/env bash
set -e

if [[ -f ".env" ]]; then
  echo "Loading environment variables from .env:"
  set -o allexport
  source ".env"
  set +o allexport
else
  echo "No .env found — please enter the values below:"

  read -rp  "POSTGRES_DB: "       POSTGRES_DB
  read -rp  "POSTGRES_USER: "     POSTGRES_USER
  read -rsp "POSTGRES_PASSWORD: " POSTGRES_PASSWORD
  read -rp  "PGADMIN_DEFAULT_EMAIL: "    PGADMIN_DEFAULT_EMAIL
  read -rsp "PGADMIN_DEFAULT_PASSWORD: " PGADMIN_DEFAULT_PASSWORD

  export POSTGRES_DB
  export POSTGRES_USER
  export POSTGRES_PASSWORD
  export PGADMIN_DEFAULT_EMAIL
  export PGADMIN_DEFAULT_PASSWORD
  echo "Required ENV variables are set up!"
  echo
fi

echo
echo "Environment:"
echo "  POSTGRES_DB=$POSTGRES_DB"
echo "  POSTGRES_USER=$POSTGRES_USER"
echo "  POSTGRES_PASSWORD=[HIDDEN]"
echo "  PGADMIN_DEFAULT_EMAIL=$PGADMIN_DEFAULT_EMAIL"
echo "  PGADMIN_DEFAULT_PASSWORD=[HIDDEN]"

docker compose -f docker-compose.yaml -p python_analytics_test up -d
