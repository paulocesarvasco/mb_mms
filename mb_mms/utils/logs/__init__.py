import os
import sys
from logging.config import dictConfig

os.makedirs('logs', exist_ok=True)

dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s][%(levelname)s][%(module)s][%(message)s]',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'error': {
            'format': '[%(asctime)s][%(levelname)s][%(module)s][%(lineno)d][%(message)s]',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'default',
            'level': 'INFO'
        },
        'file_debug': {
            'class': 'logging.FileHandler',
            'filename': 'logs/debug.log',
            'formatter': 'default',
            'level': 'DEBUG'
        },
        'file_error': {
            'class': 'logging.FileHandler',
            'filename': 'logs/error.log',
            'formatter': 'error',
            'level': 'ERROR'
        }
    },
    'loggers': {
        '': {
            'handlers': ['stdout', 'file_debug', 'file_error'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
})
