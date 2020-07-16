from flask import Blueprint

# 创建一个蓝图对象
index_blu = Blueprint('index', __name__)
from . import views
