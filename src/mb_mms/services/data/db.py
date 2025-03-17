import os

from flask import current_app, g
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from mb_mms.services.data import commands

def init_app(app):
    app.cli.add_command(commands.init_db_command)
    app.cli.add_command(commands.populate_db_command)


def get_db_engine():
    if 'db' not in g:
        g.db = create_engine(os.getenv('DB_URL', ''), echo=True)
    return g.db


def exec_migrations():
    # TODO: improve to handler more than 1 file
    with current_app.open_resource('migrations/migration_0.sql', mode='r') as f:
        stmts = f.read().strip().split(';')
        with Session(get_db_engine()) as session, session.begin():
            try:
                [session.execute(text(stmt)) for stmt in stmts if stmt != '']
                session.commit()
            except Exception as err:
                session.rollback()
                print('migration error: ', err)


def save_object(obj=None):
    with Session(get_db_engine()) as session, session.begin():
        try:
            session.add(obj)
            session.commit()
        except Exception as err:
            session.rollback()
            print('failed to save on db: ', err)
