import os
import time
import pytz
from datetime import datetime, timedelta
from flask_apscheduler import APScheduler
from tenacity import retry, wait_fixed

from mb_mms.models.pair_averages import MovingAverage
from mb_mms.services.data import db
from mb_mms.services.mb_api.mb_api import MB_API


class Scheduler:
    scheduler = APScheduler()

    def __init__(self, max_retries=10):

        self.scheduler.add_job(
            id='last_rate',
            func=self.compute_mms,
            trigger='cron',
            hour=0, minute=1, second=0,
            timezone=pytz.timezone('America/Sao_Paulo')
        )

        self.max_retries = max_retries
        self.attempts = 0

    def register_retry(self):
        self.attempts += 1
        if self.attempts > self.max_retries:
            # TODO: throw alert
            print('maximum retries reached')

    @retry(wait=wait_fixed(600))
    def compute_mms(self):
        mb = MB_API()

        end = datetime.now(pytz.timezone('America/Sao_Paulo')) - timedelta(days=1)
        start = (end - timedelta(days=200)).strftime('%Y-%m-%d')

        end_unix = int(time.mktime(datetime.strptime(end.strftime('%Y-%m-%d'), '%Y-%m-%d').timetuple()))
        start_unix = int(time.mktime(datetime.strptime(start, '%Y-%m-%d').timetuple()))

        pairs = os.getenv('PAIRS', '').split(',')

        try:
            for pair in pairs:

                rates = mb.request_rate(pair=pair, start=start_unix, end=end_unix)

                if len(rates) != 200:
                    raise Exception('missed registers')

                mms_200 = mb.mms(rates=rates)
                mms_50 = mb.mms(rates=rates[-50:])
                mms_20 = mb.mms(rates=rates[-20:])


                with db.get_db_session() as session, session.begin():
                    try:
                        obj = MovingAverage()
                        obj.pair, obj.timestamp = pair, end_unix
                        obj.mms_20, obj.mms_50, obj.mms_200 = mms_20[0], mms_50[0], mms_200[0]
                        session.add(obj)
                        session.commit()
                        print('new register added')
                    except Exception as e:
                        session.rollback()
                        raise e

        except Exception as e:
            self.register_retry()
            print(e)
            raise e
