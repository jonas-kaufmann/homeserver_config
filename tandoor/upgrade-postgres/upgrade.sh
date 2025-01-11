#!/bin/bash

set -e

# Set the path for the old PostgreSQL 11 data directory
OLD_DB_PATH=/var/lib/postgresql/11/data

# Check if the old database directory exists
if [ ! -d "$OLD_DB_PATH/base" ]; then
  echo "Old database directory not found: $OLD_DB_PATH/base"
  exit 1
fi

# Start the old PostgreSQL 11 server
echo "Starting old PostgreSQL 11 server..."
/usr/lib/postgresql/11/bin/pg_ctl -D "$OLD_DB_PATH" -o "-c listen_addresses='localhost'" start

# Wait for the server to start
sleep 5

# Create the new user role in the new PostgreSQL 11 server
echo "Creating the new user role..."
# /usr/lib/postgresql/11/bin/psql -h localhost -p 5432 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE ROLE $POSTGRES_USER LOGIN PASSWORD '$POSTGRES_PW';"

# Change ownership of old db
echo "Changing ownership of old database..."
# /usr/lib/postgresql/11/bin/psql -h localhost -p 5432 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "ALTER DATABASE $POSTGRES_DB OWNER TO $POSTGRES_USER;"


# Dump the djangodb database
echo "Dumping the old database..."
/usr/lib/postgresql/11/bin/pg_dump -h localhost -p 5432 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc > /tmp/olddb_dump.sql

# Stop the old PostgreSQL 11 server
echo "Stopping old PostgreSQL 11 server..."
/usr/lib/postgresql/11/bin/pg_ctl -D "$OLD_DB_PATH" stop

echo "Changing ownership and permissions of the new PostgreSQL 16 data directory..."
chown -R postgres:postgres /var/lib/postgresql/16/data
chmod -R 700 /var/lib/postgresql/16/data

# Initialize a new PostgreSQL 16 database cluster
echo "Initializing a new PostgreSQL 16 database cluster..."
/usr/lib/postgresql/16/bin/initdb -D /var/lib/postgresql/16/data

# Start the PostgreSQL 16 server
echo "Starting PostgreSQL 16 server..."
/usr/lib/postgresql/16/bin/pg_ctl -D /var/lib/postgresql/16/data -o "-c listen_addresses='localhost'" start

# Wait for the server to start
sleep 5

# Create the user role in the new PostgreSQL 16 server
echo "Creating the user role..."
/usr/lib/postgresql/16/bin/psql -h localhost -p 5432 -U postgres -c "CREATE ROLE $POSTGRES_USER LOGIN PASSWORD '$POSTGRES_PW';"

# Grant the djangouser role the necessary privileges to create databases
echo "Granting privileges to the user role..."
/usr/lib/postgresql/16/bin/psql -h localhost -p 5432 -U postgres -c "ALTER ROLE $POSTGRES_USER CREATEDB;"

# Create the new database in the new PostgreSQL 16 server
echo "Creating the new database..."
/usr/lib/postgresql/16/bin/createdb -h localhost -p 5432 -U $POSTGRES_USER $POSTGRES_DB

# Restore the old database dump into the new PostgreSQL 16 server
echo "Restoring the old database dump into the new PostgreSQL 16 server..."
/usr/lib/postgresql/16/bin/pg_restore -h localhost -p 5432 -U $POSTGRES_USER -d $POSTGRES_DB /tmp/olddb_dump.sql

# Modify pg_hba.conf to allow connections from the Django application
echo "Modifying pg_hba.conf..."
echo "host all all all md5" >> /var/lib/postgresql/16/data/pg_hba.conf

# Reload the PostgreSQL configuration
echo "Reloading PostgreSQL configuration..."
/usr/lib/postgresql/16/bin/pg_ctl -D /var/lib/postgresql/16/data reload

# Analyze the upgraded database
echo "Analyzing the upgraded database..."
/usr/lib/postgresql/16/bin/vacuumdb -h localhost -p 5432 -U $POSTGRES_USER --analyze $POSTGRES_DB

echo "Upgrade process completed."

# Stop the PostgreSQL 16 service
echo "Stopping PostgreSQL 16 service..."
/usr/lib/postgresql/16/bin/pg_ctl -D /var/lib/postgresql/16/data stop

# Exit the script
exit 0