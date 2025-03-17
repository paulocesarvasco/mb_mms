import os
import click
from flask import current_app, g
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session


def get_db_engine():
    if 'db' not in g:
        g.db = create_engine(os.getenv('DB_URL', ''), echo=True)
    return g.db


def exec_migrations():
    # TODO: improve to handler more than 1 file
    with current_app.open_resource('migrations/migration_0.sql', mode='r') as f:
        stmts = f.read().strip().split(';')
        with Session(get_db_engine()) as session:
            try:
                [session.execute(text(stmt)) for stmt in stmts if stmt != '']
                session.commit()
            except Exception as err:
                session.rollback()
                print('migration error: ', err)


def close_session(e=None):
    db_conn = g.pop('db', None)

    if db_conn is not None:
        db_conn.close()


@click.command('init-db')
def init_db_command():
    exec_migrations()
    click.echo('Initialized the database.')

def init_app(app):
    # app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
