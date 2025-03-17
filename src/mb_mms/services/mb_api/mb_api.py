import datetime
import os
from requests import HTTPError, Session
from http import HTTPStatus

class MB_API:
    def __init__(self) -> None:
        pass

    def request_rate(self, pair:str, start, end):
        try:
            unix_start = int(datetime.datetime.strptime(start, '%d-%m-%Y').timestamp())
            unix_end = int(datetime.datetime.strptime(end, '%d-%m-%Y').timestamp())

            url = os.getenv('MB_API', '').format(pair, unix_start, unix_end)
            session = Session()
            session.headers.update({'User-Agent': 'Dummy User Agent'})
            res = session.get(url)

            if res.status_code != HTTPStatus.OK:
                print(res.text)
                res.raise_for_status()

            return res.json()

        except ValueError as err:
            print('parameters error:', err)
        except HTTPError as err:
            print('request error:', err)
        except Exception as err:
            print('unexpected error:', err)
