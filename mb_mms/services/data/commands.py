import logging
import click
from mb_mms.services.data import db


@click.command('init-db')
def init_db_command():
    db.exec_migrations()
    logging.info('Migrations applied')
