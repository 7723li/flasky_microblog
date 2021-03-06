#程序的配置
import os
basedir = os.path.abspath(os.path.dirname(__file__))
#设置管理员邮箱地址为发送邮箱
os.environ.setdefault('FLASKY_ADMIN','li542131220@163.com')
os.environ.setdefault('FLASKY_MAIL_SENDER',os.environ.get('FLASKY_ADMIN'))
os.environ.setdefault('MAIL_PASSWORD','abc123')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = os.environ.get('FLASKY_MAIL_SENDER')
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    FLASKY_POSTS_PER_PAGE=10
    FLASKY_FOLLOWERS_PER_PAGE=10
    FLASKY_COMMENTS_PER_PAGE=10
    UPLOADED_PHOTOS_DEST=os.path.abspath(os.path.join(os.getcwd()+'\\app',"static/music"))
    MUSIC_DEST=os.path.abspath(os.path.join(os.getcwd()+'\\app',"static/Gravatar"))
    WHOOSH_BASE  = os.path.join(basedir, 'search.sqlite')
    LANGUAGES = {
    'en': 'English'
    }

    @staticmethod
    def init_app_1(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
