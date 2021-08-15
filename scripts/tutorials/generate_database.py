# Script to generate database from JSON contents
# This gets run automatically with Github Actions

import sys
import os
from astrodbkit2.astrodb import create_database, Database
sys.path.append(os.getcwd())  # hack to be able to discover simple
from simple.schema import *

# Location of source data
DB_PATH = 'data'
DB_NAME = 'SIMPLE.db'

# Used to overwrite AstrodbKit2 reference tables defaults
REFERENCE_TABLES = ['Publications', 'Telescopes', 'Instruments', 'Modes', 'PhotometryFilters']


def load_postgres(connection_string):
    # For Postgres, we connect and drop all database tables

    # Fix for SQLAlchemy 1.4.x
    if connection_string.startswith("postgres://"):
        connection_string = connection_string.replace("postgres://", "postgresql://", 1)

    try:
        db = Database(connection_string)
        db.base.metadata.drop_all()
        db.session.close()
        db.engine.dispose()
    except RuntimeError:
        # Database already empty or doesn't yet exist
        pass

    # Proceed to load the database
    load_database(connection_string)


def load_sqlite():
    # First, remove the existing database in order to recreate it from the schema
    # If the schema has not changed, this part can be skipped
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    connection_string = 'sqlite:///' + DB_NAME

    # Proceed to load the database
    load_database(connection_string)


def load_database(connection_string):
    # Create and load the database
    create_database(connection_string)

    # Now that the database is created, connect to it and load up the JSON data
    db = Database(connection_string, reference_tables=REFERENCE_TABLES)
    db.load_database(DB_PATH, verbose=False)

    print('New database generated.')

    # Close all connections
    db.session.close()
    db.engine.dispose()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        architecture = sys.argv[1].lower()
        if architecture == 'postgres':
            if len(sys.argv) > 2:
                connection_string = sys.argv[2]
            else:
                connection_string = os.getenv('SIMPLE_DATABASE_URL')
            load_postgres(connection_string)
        elif architecture == 'sqlite':
            load_sqlite()
        else:
            print(f'Unrecognized architecture: {architecture}')
    else:
        print('Specify database architecture (eg, postgres, sqlite)')
