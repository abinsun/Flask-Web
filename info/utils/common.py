# 共用的自定义工具类
import functools

from flask import session, current_app, g

from info.models import User


def do_index_class(index):
    """返回指定索引对应的类名"""
    if index == 0:
        return "first"
    elif index == 1:
        return "second"
    elif index == 2:
        return "third"
    else:
        return ""


def user_login_data(f):
    # 使用functools.wraps去装饰内层函数可以保持当前装饰器去装饰的函数的__name__不变
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # 显示用户是否登录的逻辑
        # 获取用户id
        user_id = session.get("user_id", None)
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        g.user = user
        return f(*args, **kwargs)
    return wrapper


