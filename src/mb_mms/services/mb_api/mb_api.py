import os
from requests import HTTPError, Session
from http import HTTPStatus

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

    def calculate_mms(self, rates=None, delta=30):
        assert rates is not None
        mms = []
        for idx in range(len(rates)):
            if idx < delta:
                mms.append((rates[idx][1], None))
                continue
            slice_rates = rates[idx-delta:idx]
            mms.append((rates[idx][1], sum([register[0] for register in slice_rates])/delta))
        return mms
