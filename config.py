import logging
import redis


class Config(object):
    """工程配置信息"""
    # DEBUG = True
    SECRET_KEY = 'j7g+RfhBHm5vlJKhWNOsqm9Jha0y536EQNE6Fw5TNQHyuylYkOVraAwxzMyrxYeX'

    """为数据库添加配置"""
    SQLALCHEMY_DATABASE_URI="mysql://root:@127.0.0.1:3306/python"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 在请求结束时，如果指定配置为True，那么SQLALCHEMY会自动执行db.session.commit()操作
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    """redis配置"""
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    """flask_session配置"""
    SESSION_TYPE = 'redis'  # Session保存位置
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 设置Session保存指定位置
    SESSION_USE_SIGNER = True  # 开启Session签名
    SESSION_PERMANENT = False  # 设置需要过期时间,而不是永久
    PERMANENT_SESSION_LIFETIME = 86400 * 2  # 设置过期时间为2天

    # 设置日志等级
    LOG_LEVEl = logging.ERROR


class DevelopementConfig(Config):
    """开发模式下的配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产模式下的配置"""
    DEBUG = False
    LOG_LEVEl = logging.WARNING


class TestingConfig(Config):
    """单元测试下的配置"""
    DEBUG = True
    TESTING = True


config = {
    "development": DevelopementConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
