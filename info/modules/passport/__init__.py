# 登录注册的相关业务逻辑都在此模块中
from flask import Blueprint

# 创建一个蓝图对象
passport_blu = Blueprint('passport', __name__, url_prefix="/passport")
from . import views
