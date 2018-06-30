import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chycjclb'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    PYBLOG_MAIL_SUBJECT_PREFIX = '[PyBlog]'
    PYBLOG_MAIL_SENDER = 'PyBlog Admin <admin@pyblog.com>'
    PYBLOG_ADMIN = os.environ.get('PYBLOG_ADMIN')
    CACHE_TYPE = 'simple'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost/pyblog"


config = {
    'development': DevelopmentConfig,

    'default': DevelopmentConfig
}
