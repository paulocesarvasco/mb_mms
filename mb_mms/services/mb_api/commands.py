import os
import click
import time
import pytz

from datetime import datetime, timedelta
from mb_mms.models.pair_averages import MovingAverage
from mb_mms.services.data import db
from mb_mms.services.mb_api.mb_api import MB_API
from sqlalchemy.orm import Session


@click.command('populate-db')
def populate_db():
    """
    Populates the database with historical rate data and calculated moving averages (MMS) for specified currency pairs.

    This command performs the following steps:
    1. Initializes the MB_API instance to interact with the API.
    2. Sets the time range for data retrieval (1 year ago).
    3. Converts the time range to Unix timestamps.
    4. Retrieves the list of currency pairs from the environment variable `PAIRS`.
    5. For each currency pair:
       - Fetches the historical rate data within the specified time range.
       - Calculates the 20-day, 50-day, and 200-day sliding moving averages (MMS).
       - Ensures the lengths of the MMS lists are consistent.
       - Inserts the calculated MMS values and timestamps into the database.
    6. Handles errors during database insertion and rolls back the transaction if necessary.
    7. Outputs a success message if the database is populated successfully.

    Environment Variables:
        - `PAIRS`: A comma-separated list of currency pairs to process (e.g., 'BRLBTC,BRLETH').
        - `MB_API`: The API endpoint format for fetching rate data.

    Raises:
        - Displays an error message if the lengths of the MMS lists are inconsistent.
        - Displays an error message if an exception occurs during database insertion.

    Outputs:
        - Success message: 'Database populated.'
        - Error messages: In case of inconsistencies or exceptions.
    """
    mb = MB_API()
    end_time = datetime.now(pytz.timezone('America/Sao_Paulo')) - timedelta(days=1)
    start_time = (end_time - timedelta(days=365)).strftime('%Y-%m-%d')

    end_time_unix = int(time.mktime(datetime.strptime(end_time.strftime('%Y-%m-%d'), '%Y-%m-%d').timetuple()))
    start_time_unix = int(time.mktime(datetime.strptime(start_time, '%Y-%m-%d').timetuple()))

    pairs = os.getenv('PAIRS', '').split(',')

    for pair in pairs:
        rates = mb.request_rate(pair=pair, start=start_time_unix, end=end_time_unix)
        mms_20 = mb.sliding_mms(delta=20, rates=rates)
        mms_50 = mb.sliding_mms(delta=50, rates=rates)
        mms_200 = mb.sliding_mms(delta=200, rates=rates)

        if len(mms_20) != len(mms_50) != len(mms_200):
            click.echo(message='inconsistent rates', err=True)
            return

        with Session(db.get_db_engine()) as session, session.begin():
            try:
                for idx in range(len(mms_20)):
                    obj = MovingAverage()
                    obj.mms_20, obj.mms_50, obj.mms_200 = mms_20[idx][0], mms_50[idx][0], mms_200[idx][0]
                    obj.timestamp, obj.pair = mms_20[idx][1], pair
                    session.add(obj)
                session.commit()
            except Exception as err:
                session.rollback()
                click.echo(message=err, err=True, color=True)
                return

    click.echo('Database populated.')
