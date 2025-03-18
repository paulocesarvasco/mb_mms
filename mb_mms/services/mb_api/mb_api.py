import os
from typing import Any, List, Tuple
from requests import  HTTPError, Session
from http import HTTPStatus
from sqlalchemy import select

from mb_mms.models.pair_averages import MovingAverage
from mb_mms.services.data import db

class MB_API:
    """
    A class to interact with the MB API and perform operations related to rates and moving averages.
    """

    def __init__(self) -> None:
        """
        Initializes the MB_API class.
        """
        pass

    def request_rate(self, pair: str, start, end):
        """
        Fetches the rate data for a given currency pair within a specified time range.

        Args:
            pair (str): The currency pair for which the rate data is requested.
            start: The start timestamp for the data range.
            end: The end timestamp for the data range.

        Returns:
            List[Tuple[float, int]]: A list of tuples containing the closing rate and timestamp for each data point.
                                     Returns an empty list if an error occurs.
        """
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
            return []
        except HTTPError as err:
            print('request error:', err)
            return []
        except Exception as err:
            print('unexpected error:', err)
            return []

    def mms(self, rates: List[Tuple[Any, Any]]):
        """
        Calculates the Mean Moving Average (MMS) for a given list of rates.

        Args:
            rates (List[Tuple[Any, Any]]): A list of tuples containing the rate and timestamp.

        Returns:
            Tuple[float, Any]: A tuple containing the calculated MMS and the timestamp of the last rate.
                              Returns (0, 0) if the rates list is empty.
        """
        if len(rates) == 0:
            return (0, 0)

        return (sum([rate[0] for rate in rates]) / len(rates), rates[len(rates) - 1][1])

    def sliding_mms(self, delta: int, rates=None):
        """
        Calculates the sliding Mean Moving Average (MMS) over a specified window size.

        Args:
            delta (int): The window size for the sliding MMS calculation.
            rates (List[Tuple[Any, Any]], optional): A list of tuples containing the rate and timestamp.
                                                    Defaults to None.

        Returns:
            List[Tuple[Optional[float], Any]]: A list of tuples containing the calculated MMS and timestamp.
                                               Returns an empty list if an error occurs or if delta is less than 1.
        """
        assert rates is not None
        if delta < 1:
            return []

        mms = []
        delta_offset = delta - 1
        try:
            for idx in range(len(rates)):
                if idx < delta_offset:
                    mms.append((None, rates[idx][1]))
                    continue
                slice_rates = rates[idx - delta_offset:idx + 1]
                mms.append(self.mms(slice_rates))
            return mms
        except Exception as err:
            print(err)
            return []

    def search_mms(self, pair: str, start: int, end: int, precision: int):
        """
        Searches for the Mean Moving Average (MMS) data for a given currency pair and time range.

        Args:
            pair (str): The currency pair for which the MMS data is requested.
            start (int): The start timestamp for the data range.
            end (int): The end timestamp for the data range.
            precision (int): The precision of the MMS data (e.g., 20, 50, 200).

        Returns:
            List[Dict]: A list of dictionaries containing the timestamp and MMS value.
                        Raises a ValueError if the precision is not supported.

        Raises:
            ValueError: If the precision value is not supported.
        """
        with db.get_db_engine().connect() as conn:
            match precision:
                case 20:
                    stmt = (
                        select(MovingAverage.timestamp, MovingAverage.mms_20.label('mms'))
                        .where(MovingAverage.pair == pair)
                        .where(MovingAverage.timestamp.between(start, end))
                    )
                case 50:
                    stmt = (
                        select(MovingAverage.timestamp, MovingAverage.mms_50.label('mms'))
                        .where(MovingAverage.pair == pair)
                        .where(MovingAverage.timestamp.between(start, end))
                    )
                case 200:
                    stmt = (
                        select(MovingAverage.timestamp, MovingAverage.mms_200.label('mms'))
                        .where(MovingAverage.pair == pair)
                        .where(MovingAverage.timestamp.between(start, end))
                    )
                case _:
                    raise ValueError
            res = conn.execute(stmt).all()
            return [r._asdict() for r in res]
