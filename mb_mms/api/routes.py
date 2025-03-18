from http import HTTPStatus
import time
from datetime import datetime, timedelta
from flask import jsonify
from mb_mms.services.mb_api import mb_api
from . import currency_bp
from flask import request

@currency_bp.route('/', methods=['GET'])
def root():
    return '<p>Currency MMS initial page!</p>'


@currency_bp.route('/<pair>/mms', methods=['GET'])
def search(pair):
    mb = mb_api.MB_API()

    default = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    default_unix = int(time.mktime(datetime.strptime(default, "%Y-%m-%d").timetuple()))

    try:
        precision = request.args.get('precision', type=str)
        start = request.args.get('from', type=int)
        end = request.args.get('to', type=int, default=default_unix)

        if precision is None or start is None or end is None:
            raise ValueError

        precision = int(precision[:-1])
        res = mb.search_mms(pair=pair, start=start, end=end, precision=precision)

        return jsonify(res)

    except Exception as err:
        return str(err), HTTPStatus.INTERNAL_SERVER_ERROR
