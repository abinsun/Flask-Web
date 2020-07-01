from flask_wtf import FlaskForm
from wtforms import  StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired, EqualTo, Email, Regexp, Length

class LoginForm(FlaskForm):
    username= StringField(label='用户名',validators=[DataRequired()])
    password= PasswordField(label='密码',validators=[DataRequired()])
    submit=SubmitField(label='提交')

class RegistrationForm(FlaskForm):
    username= StringField(label='用户名',validators=[DataRequired(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9.]*$',0,'用户名必须由字母数字下划线或.组成')])
    password1= PasswordField(label='密码',validators=[DataRequired()])
    password= PasswordField(label='确认密码',validators=[DataRequired(),EqualTo('password1', message='两次需一致')])
    email=StringField(label='email', validators=[Email()])
    submit=SubmitField(label='注册')
 