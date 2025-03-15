from . import currency_bp

@currency_bp.route('/', methods=['GET'])
def root():
    return '<p>Currency MMS initial page!</p>'
