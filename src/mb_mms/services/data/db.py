import os
import click
import mariadb
from flask import current_app, g

def get_db():
    if 'db' not in g:
        conn_params = {
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'database': os.getenv('DB_DATABASE')
        }
        g.db = mariadb.connect(**conn_params)
    return g.db


def exec_migrations():
    c = get_db().cursor()

    # TODO: improve to handler more than 1 file
    with current_app.open_resource('migrations/migration_0.sql', mode='r') as f:
        stats = f.read().strip().split(';')
        [c.execute(stat) for stat in stats if stat != '']


def close_db(e=None):
    db_conn = g.pop('db', None)

    if db_conn is not None:
        db_conn.close()


@click.command('init-db')
def init_db_command():
    exec_migrations()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
