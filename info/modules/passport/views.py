import re
import random
from datetime import datetime

from flask import request, abort, current_app, make_response, jsonify, session

from . import passport_blu
from info.utils.captcha.captcha import captcha
from ... import redis_store, constants, db
from ...libs.yuntongxun.sms import CCP
from ...models import User
from ...utils.response_code import RET


@passport_blu.route('/logout')
def logout():
    """
    退出登录
    :return:
    """
    # pop是移除session中的数据(dict),pop会有一个返回值，如果移除的key不存在返回None
    session.pop('user_id', None)
    session.pop('mobile', None)
    session.pop('nick_name', None)
    # 要清除is_admin的session值,不然登录管理员后退出再登录普通用户又能访问管理员后台
    session.pop('is_admin', None)
    return jsonify(errno=RET.OK, errmsg="退出成功")


@passport_blu.route('/login', methods=["POST"])
def login():
    """
    登录逻辑
    1.获取参数
    2.校验参数
    3.校验密码是否正确
    4.如果正确，保存用户登录状态
    5.返回响应
    :return:
    """
    # 1.获取参数
    params_dict = request.json
    mobile = params_dict.get("mobile")
    password = params_dict.get("password")
    # 2.校验参数
    if not all([mobile, mobile]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 校验手机参数(参数是否符合规则，判断是否有值)
    if not re.match("^1[3578][0-9]{9}$", mobile):
        # 提示手机号不正确
        return jsonify(errno=RET.PARAMERR, errmsg="手机号不正确")

    # 3.校验密码是否正确
    # 从数据库查询当前是否有指定手机号的用户
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据错误")
    if not user:
        return jsonify(errno=RET.USERERR, errmsg="用户不存在")
    # 校验密码
    if not user.check_passowrd(password):
        return jsonify(errno=RET.PWDERR, errmsg="密码错误")

    # 4.如果正确，保存用户登录状态
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile
    # 记录用户最后一次登录时间
    user.last_login = datetime.now()

    # 如果在视图函数中对模型的属性有修改，那么需要commit到数据库保存
    # 但是其实可以不用自己去写db.session.commit(),前提是对SQLAlchemy有过相关配置
    # try:
    #     db.session.commit()
    # except Exception as e:
    #     db.session.rollback()
    #     current_app.logger.error(e)

    # 5.返回响应
    return jsonify(errno=RET.OK, errmsg="登录成功")


@passport_blu.route('/register', methods=["POST"])
def register():
    """
    注册逻辑
    1.获取参数
    2.校验参数
    3.取到服务器保存的真实短信验证码内容
    4.校验用户输入的短信验证码与真实短信验证码是否一致
    5.如果一致，初始化User模型，并且赋值属性
    6.将user模型添加到数据库
    7.返回响应
    :return:
    """
    # 1.获取参数
    param_dict = request.json
    mobile = param_dict.get("mobile")
    sms_code = param_dict.get("smscode")
    password = param_dict.get("password")

    # 2.校验参数
    if not all([mobile, sms_code, password]):
        # 参数不全
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 校验手机参数(参数是否符合规则，判断是否有值)
    if not re.match("^1[3578][0-9]{9}$", mobile):
        # 提示手机号不正确
        return jsonify(errno=RET.PARAMERR, errmsg="手机号不正确")

    # 3.取到服务器保存的真实短信验证码内容
    try:
        real_sms_code = redis_store.get("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
        # 获取本地验证码失败
        return jsonify(errno=RET.DBERR, errmsg="获取本地验证码失败")
    if not real_sms_code:
        # 短信验证码过期
        return jsonify(errno=RET.NODATA, errmsg="短信验证码过期")

    # 4.校验用户输入的短信验证码与真实短信验证码是否一致
    if sms_code != real_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 5.如果一致，初始化User模型，并且赋值属性
    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    # 记录用户最后一次登录时间
    user.last_login = datetime.now()
    # 对密码进行处理
    user.password = password

    # 6.将user模型添加到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        # 数据保存错误
        return jsonify(errno=RET.DATAERR, errmsg="数据保存错误")

    # 往session中保存数据表示当前已经登录
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile

    # 7. 返回注册结果
    return jsonify(errno=RET.OK, errmsg="注册成功")


@passport_blu.route('/sms_code', methods=["POST"])
def send_msg_code():
    """
    发送短信逻辑
    1.获取用户输入的参数：手机号，图片验证码内容，图片验证码编号(随机值)
    2.校验参数(参数是否符合规则，判断是否有值)
    3.从redis中取出真实的验证码内容
    4.与用户的验证码内容进行对比，如果不一致，返回验证码输入错误
    # 4.1. 校验该手机是否已经注册
    5.如果一致，生成验证码内容(随机数据)
    6.发送短信验证码
    7.redis中保存短信验证码内容
    8.告知发送结果
    :return:
    """
    # 1.获取用户输入的参数：手机号，图片验证码内容，图片验证码编号(随机值)
    param_dict = request.json
    mobile = param_dict.get('mobile')
    image_code = param_dict.get('image_code')
    image_code_id = param_dict.get('image_code_id')
    if not all([mobile, image_code_id, image_code]):
        # 参数不全
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    # 2.校验参数(参数是否符合规则，判断是否有值)
    if not re.match("^1[3578][0-9]{9}$", mobile):
        # 提示手机号不正确
        return jsonify(errno=RET.DATAERR, errmsg="手机号不正确")
    # 3.从redis中取出真实的验证码内容
    try:
        real_image_code = redis_store.get("ImageCodeId_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(RET.DBERR, errmsg="数据查询失败")
    #  判断验证码是否存在，已过期
    if not real_image_code:
        return jsonify(RET.NODATA, errmsg="图片验证码过期")
    # 4.与用户的验证码内容进行对比，如果不一致，返回验证码输入错误
    if real_image_code.upper() != image_code.upper():
        return jsonify(RET.DATAERR, errmsg="验证码输入错误")
    # 4.1. 校验该手机是否已经注册
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    # if user:
    #     # 该手机已被注册
    #     return jsonify(errno=RET.DATAEXIST, errmsg="该手机已被注册")
    # 5.如果一致，生成验证码内容(随机数据)
    result = random.randint(0, 999999)
    sms_code = "%06d" % result
    print("短信验证码的内容：%s" % sms_code)
    current_app.logger.debug("短信验证码的内容：%s" % sms_code)
    result = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES / 60], "1")
    # 6.发送短信验证码
    if result != 0:
        # 发送短信失败
        return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")
    # 7.redis中保存短信验证码内容
    try:
        redis_store.set("SMS_" + mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        # 保存短信验证码失败
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码失败")
    # 8.告知发送结果
    return jsonify(errno=RET.OK, errmsg="发送短信成功")


@passport_blu.route('/image_code')
def get_image_code():
    """
    生成图片验证码并返回
    1.获取到当前的图片编号id
    2.判断参数是否有值
    3.生成验证码
    4.保存图片验证码文字内容到redis
    5.返回图片
    :return:
    """
    # 1.取到参数
    image_code_id = request.args.get('imageCodeId', None)
    # 2.判断参数是否有值
    if not image_code_id:
        return abort(403)
    # 3.生成图片验证码
    name, text, image = captcha.generate_captcha()
    print("图片验证码是%s" % text)
    # 4.保存图片验证码文字内容到redis
    try:
        # 保存当前生成的图片验证码内容
        redis_store.set('ImageCodeId_' + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
    # 返回响应内容
    resp = make_response(image)
    # 设置内容类型,以便浏览器更加只能识别其是什么类型
    resp.headers['Content-Type'] = 'image/jpg'
    return resp
