set -eu

if [ "$CLASSIFIER_POSTGRES_TEST_DB" = "$POSTGRES_DB" ]; then
    printf '%s\n' "CLASSIFIER_POSTGRES_TEST_DB must differ from POSTGRES_DB" >&2
    exit 1
fi

psql \
    --set=ON_ERROR_STOP=1 \
    --username "$POSTGRES_USER" \
    --dbname "$POSTGRES_DB" \
    --set=test_database="$CLASSIFIER_POSTGRES_TEST_DB" <<'SQL'
SELECT format('CREATE DATABASE %I', :'test_database')
WHERE NOT EXISTS (
    SELECT 1
    FROM pg_database
    WHERE datname = :'test_database'
)
\gexec
SQL
