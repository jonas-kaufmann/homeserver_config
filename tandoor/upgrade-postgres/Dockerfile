FROM postgres:16

# Set environment variables
ENV POSTGRES_USER=django_tandoor
ENV POSTGRES_PW=aS1TLY03x9gxxdql3n/W52wKmpgCHWyeVwodjn6N
ENV POSTGRES_DB=djangodb

# Install necessary packages
RUN apt-get update && apt-get install -y \
    postgresql-11 \
    postgresql-client-11 \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Change the UID of the existing postgres user to 70
RUN usermod -u 70 postgres

# Create the new data directory for PostgreSQL 16
RUN mkdir -p /var/lib/postgresql/16/data

# Copy the upgrade script
COPY upgrade.sh /usr/local/bin/

# Set execute permission on the script
RUN chmod +x /usr/local/bin/upgrade.sh

# Change ownership and permissions of the /var/lib/postgresql directory as root
RUN sudo chown -R postgres:postgres /var/lib/postgresql && \
    sudo chmod -R 700 /var/lib/postgresql

USER postgres

# Set the entrypoint
ENTRYPOINT ["/usr/local/bin/upgrade.sh"]