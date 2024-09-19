#!/usr/bin/env bash
# wait-for-it.sh

host="$1"
shift
cmd="$@"

#!/bin/bash
until pg_isready -h postgres -p 5432 -U $PG_USERNAME; do
    echo "Postgres is unavailable - sleeping"
    sleep 2
done

>&2 echo "Postgres is up - executing command"
exec $cmd