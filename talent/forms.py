from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields.simple import StringField, TextAreaField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email

class signupForm(FlaskForm):
    userid = StringField('useid', validators=[DataRequired("ID는 필수입력 항목입니다"), Length(min=3, max=25)])
    password = PasswordField('password', validators=[DataRequired("비밀번호는 8~20자 필수입력 항목입니다")])
    password1 = PasswordField('password_confirm', validators=[DataRequired("비밀번호를 다시 입력해주세요"),EqualTo('password',message="비밀번호가 일치하지 않습니다.")])
    name = StringField('name', validators=[DataRequired("이름을 입력해 주세요"), Length(min=2, max=10)])
    email = EmailField('email', validators=[DataRequired("이메일 주소를 입력해주세요")])
    phone = StringField('phone', validators=[DataRequired("전화번호를 입력해주세요")])
    birth = StringField('birth', validators=[DataRequired()])
