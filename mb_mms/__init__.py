from flask import Flask
from dotenv import load_dotenv
import mb_mms.utils.logs as _

def create_app():
    app = Flask(__name__)

    load_dotenv()

    from mb_mms.api.routes import currency_bp
    app.register_blueprint(currency_bp)


    from mb_mms.services.data import commands as db_commands
    app.cli.add_command(db_commands.init_db_command)

    from mb_mms.services.mb_api import commands as mb_commads
    app.cli.add_command(mb_commads.populate_db)

    from mb_mms.services.job.scheduler import Scheduler
    app.config['SCHEDULER_API_ENABLED'] = True
    s = Scheduler(app)
    s.scheduler.start()

    app.logger.info('Application initialized')
    return app
