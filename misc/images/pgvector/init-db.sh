#!/bin/bash
set -e

# Create the pgvector extension using the superuser
echo "Creating extension ..."
PGPASSWORD=$POSTGRES_INITSCRIPTS_PASSWORD psql -v ON_ERROR_STOP=1 --username "$POSTGRES_INITSCRIPTS_USERNAME" --dbname "$POSTGRESQL_DATABASE" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS vector;
EOSQL
echo "Done creating extension ..."
