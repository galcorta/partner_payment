# -*- coding: utf-8 -*-


class LoggerConfig:
    dictConfig = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {'format': '%(asctime)s|%(levelname)s|'
                          '%(message)s|[in %(pathname)s:%(lineno)d]',
                         'datefmt': '%Y-%m-%d %H:%M:%S'},
            'short': {'format': '%(message)s'}
        },
        'handlers': {
            'default': {
                'level': 'DEBUG',
                'formatter': 'standard',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'payment_api.log',
                'maxBytes': 5000000,
                'backupCount': 10
            },
            'debug': {
                'level': 'DEBUG',
                'formatter': 'standard',
                'class': 'logging.StreamHandler'
            },
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG'
            },
        },
        'loggers': {
            'payment_api': {
                'handlers': ['default'],
                'level': 'DEBUG',
                'propagate': True},
            'werkzeug': {'propagate': True},
        },
        # 'root': { 'level': 'DEBUG', 'handlers': ['console'] }
    }
