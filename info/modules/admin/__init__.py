from flask import Blueprint, session, redirect, request, url_for

admin_blu = Blueprint("admin", __name__, url_prefix="/admin")

from . import views


@admin_blu.before_request
def check_admin():
    # if 不是管理员，跳转主页
    is_admin = session.get("is_admin", False)
    # 假如不是管理员and当前访问的不是管理员登录页
    if not is_admin and not request.url.endswith(url_for("admin.login")):
        return redirect("/")

