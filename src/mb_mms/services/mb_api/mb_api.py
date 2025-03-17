import os
from requests import  HTTPError, Session
from http import HTTPStatus
from sqlalchemy import select

from mb_mms.models.pair_averages import MovingAverage
from mb_mms.services.data import db

class MB_API:
    def __init__(self) -> None:
        pass


    def request_rate(self, pair:str, start, end):
        try:
            url = os.getenv('MB_API', '').format(pair, start, end)
            session = Session()
            session.headers.update({'User-Agent': 'Dummy User Agent'})
            res = session.get(url)

            if res.status_code != HTTPStatus.OK:
                print(res.text)
                res.raise_for_status()

            data = res.json()
            return [(register['close'], register['timestamp']) for register in data['candles']]

        except ValueError as err:
            print('parameters error:', err)
        except HTTPError as err:
            print('request error:', err)
        except Exception as err:
            print('unexpected error:', err)


    def calculate_mms(self, delta:int, rates=None):
        assert rates is not None
        mms = []
        delta_offset = delta - 1
        try:
            for idx in range(len(rates)):
                if idx < delta_offset:
                    mms.append((None, rates[idx][1]))
                    continue
                slice_rates = rates[idx-delta_offset:idx]
                mms.append((sum([register[0] for register in slice_rates])/delta, rates[idx][1]))
            return mms
        except Exception as err:
            print(err)
            return []

    def search_mms(self, pair:str, start:int, end:int, precision:int):

        with db.get_db_engine().connect() as conn:
            match precision:
                case 20:
                    stmt = (
                        select(MovingAverage.timestamp, MovingAverage.mms_20)
                        .where(MovingAverage.pair == pair)
                        .where(MovingAverage.timestamp.between(start, end))
                    )
                case 50:
                    stmt = (
                        select(MovingAverage.timestamp, MovingAverage.mms_50)
                        .where(MovingAverage.pair == pair)
                        .where(MovingAverage.timestamp.between(start, end))
                    )
                case 200:
                    stmt = (
                        select(MovingAverage.timestamp, MovingAverage.mms_200)
                        .where(MovingAverage.pair == pair)
                        .where(MovingAverage.timestamp.between(start, end))
                        )
                case _:
                    raise ValueError
            res = conn.execute(stmt).all()
            return [r._asdict() for r in res]
