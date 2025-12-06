#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres <<-EOSQL
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${POSTGRES_USER}') THEN
      CREATE USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';
   END IF;
END
\$\$;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres <<-EOSQL
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '${POSTGRES_DB}') THEN
      CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER};
   END IF;
END
\$\$;
EOSQL