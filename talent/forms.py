# talent/forms.py
import datetime as dt
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import (
    StringField, PasswordField, SelectField, SubmitField, BooleanField,
    TextAreaField, FileField, IntegerField
)
from wtforms.fields import EmailField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp

# ---------------- Constants ----------------
_THIS_YEAR = dt.date.today().year
_YEAR_START = 1950

_USERID_RE   = r'^[A-Za-z0-9_]{6,20}$'
_PASSWORD_RE = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])[A-Za-z\d!@#$%^&*(),.?":{}|<>]{8,20}$'
_PHONE_RE    = r'^\d{9,11}$'

SERVICE_CHOICES  = [
    ('', '서비스를 선택하세요'),
    ('청소', '청소'), ('과외', '과외'), ('인테리어', '인테리어'), ('디자인', '디자인'), ('이사', '이사')
]
LOCATION_CHOICES = [
    ('', '지역을 선택하세요'),
    ('서울', '서울'), ('경기', '경기'), ('부산', '부산'), ('대구', '대구'), ('기타', '기타')
]

# ---------------- Helpers ----------------
def _year_choices():
    return [(y, str(y)) for y in range(_YEAR_START, _THIS_YEAR + 1)]

def _month_choices():
    return [(m, str(m)) for m in range(1, 13)]

def _day_choices():
    return [(d, str(d)) for d in range(1, 32)]

# ---------------- Signup ----------------
class SignupForm(FlaskForm):
    userid = StringField(
        '아이디',
        validators=[DataRequired('ID는 필수입력 항목입니다'),
                    Regexp(_USERID_RE, message='아이디는 영문/숫자/밑줄 6~20자여야 합니다.')],
        render_kw={'id': 'userid', 'placeholder': '아이디 (영문/숫자/_ 6~20자)'}
    )
    password = PasswordField(
        '비밀번호',
        validators=[DataRequired('비밀번호는 필수입력 항목입니다'),
                    Regexp(_PASSWORD_RE, message='영문, 숫자, 특수문자 포함 8~20자')],
        render_kw={'id': 'password', 'placeholder': '영문·숫자·특수문자 포함 8~20자'}
    )
    password_confirm = PasswordField(
        '비밀번호 확인',
        validators=[DataRequired('비밀번호를 다시 입력해주세요'),
                    EqualTo('password', message='비밀번호가 일치하지 않습니다.')],
        render_kw={'id': 'password_confirm', 'placeholder': '비밀번호를 다시 입력'}
    )
    name = StringField(
        '이름',
        validators=[DataRequired('이름을 입력해 주세요'),
                    Length(min=2, max=10, message='이름은 2~10자')],
        render_kw={'id': 'name', 'placeholder': '이름을 입력해주세요'}
    )
    email = EmailField(
        '이메일',
        validators=[DataRequired('이메일 주소를 입력해주세요'),
                    Email(message='이메일 형식이 올바르지 않습니다.')],
        render_kw={'id': 'email', 'placeholder': '이메일 주소를 입력해주세요'}
    )
    phone = StringField(
        '전화번호',
        validators=[DataRequired('전화번호를 입력해주세요'),
                    Regexp(_PHONE_RE, message='전화번호는 숫자 9~11자리입니다.')],
        render_kw={'id': 'tel_number', 'placeholder': '숫자만 입력 (예: 01012345678)'}
    )
    birth_year  = SelectField('생년', choices=_year_choices(),  coerce=int,
                              validators=[DataRequired()], render_kw={'id': 'birth_year'})
    birth_month = SelectField('월',   choices=_month_choices(), coerce=int,
                              validators=[DataRequired()], render_kw={'id': 'birth_month'})
    birth_day   = SelectField('일',   choices=_day_choices(),   coerce=int,
                              validators=[DataRequired()], render_kw={'id': 'birth_day'})
    submit = SubmitField('회원가입')

    # 호환성: auth_views에서 password1/password2 접근을 지원
    @property
    def password1(self):
        return self.password

    @property
    def password2(self):
        return self.password_confirm

    def validate(self, extra_validators=None):
        ok = super().validate(extra_validators=extra_validators)
        if not ok:
            return False
        y, m, d = self.birth_year.data, self.birth_month.data, self.birth_day.data
        try:
            dt.date(y, m, d)
        except ValueError:
            self.birth_year.errors.append('유효하지 않은 생년월일입니다.')
            return False
        if y > _THIS_YEAR:
            self.birth_year.errors.append('유효하지 않은 생년월일입니다.')
            return False
        return True

# ---------------- Edit Profile ----------------
class EditProfileForm(FlaskForm):
    name = StringField(
        '이름', validators=[DataRequired(), Length(min=2, max=10)],
        render_kw={'id': 'name', 'placeholder': '이름'}
    )
    email = EmailField(
        '이메일', validators=[DataRequired(), Email()],
        render_kw={'id': 'email', 'placeholder': '이메일'}
    )
    tel_number = StringField(
        '전화번호', validators=[DataRequired(), Regexp(_PHONE_RE, message='전화번호는 숫자 9~11자리')],
        render_kw={'id': 'tel_number', 'placeholder': '전화번호'}
    )
    service  = StringField('제공 서비스', render_kw={'id': 'service', 'placeholder': '서비스'})
    location = StringField('활동 지역',   render_kw={'id': 'location', 'placeholder': '지역'})
    submit = SubmitField('정보 수정')

# ---------------- Expert Signup ----------------
class ExpertSignupForm(FlaskForm):
    userid = StringField(
        '아이디',
        validators=[DataRequired(), Regexp(_USERID_RE)],
        render_kw={'id': 'userid', 'placeholder': '영문/숫자/_ 6~20자', 'autocomplete': 'username'}
    )
    name = StringField('이름', validators=[DataRequired()], render_kw={'id': 'name'})
    email = EmailField('이메일', validators=[DataRequired(), Email()],
                       render_kw={'id': 'email', 'autocomplete': 'email'})
    password = PasswordField(
        '비밀번호',
        validators=[DataRequired(), Regexp(_PASSWORD_RE)],
        render_kw={'id': 'password', 'placeholder': '영문·숫자·특수문자 포함 8~20자', 'autocomplete': 'new-password'}
    )
    password_confirm = PasswordField(
        '비밀번호 확인',
        validators=[DataRequired(), EqualTo('password', message='비밀번호가 일치하지 않습니다.')],
        render_kw={'id': 'password_confirm', 'placeholder': '비밀번호 재입력', 'autocomplete': 'new-password'}
    )
    tel_number = StringField(
        '전화번호', validators=[DataRequired(), Regexp(_PHONE_RE)],
        render_kw={'id': 'tel_number', 'placeholder': '- 없이 숫자만'}
    )
    birth_year  = SelectField('년도', choices=_year_choices(),  coerce=int,
                              validators=[DataRequired()], render_kw={'id': 'birth_year'})
    birth_month = SelectField('월',   choices=_month_choices(), coerce=int,
                              validators=[DataRequired()], render_kw={'id': 'birth_month'})
    birth_day   = SelectField('일',   choices=_day_choices(),   coerce=int,
                              validators=[DataRequired()], render_kw={'id': 'birth_day'})
    service  = SelectField('제공 서비스', choices=SERVICE_CHOICES, validators=[DataRequired()],
                           render_kw={'id': 'service'})
    location = SelectField('지역', choices=LOCATION_CHOICES, validators=[DataRequired()],
                           render_kw={'id': 'location'})
    agree = BooleanField('약관 동의', validators=[DataRequired()], render_kw={'id': 'agree'})
    submit = SubmitField('매칭허브 전문가 가입하기')

# ---------------- Find ID ----------------
class FindIdForm(FlaskForm):
    name = StringField('이름', validators=[DataRequired('이름을 입력해주세요')],
                       render_kw={'id': 'name', 'placeholder': '이름'})
    email = EmailField('이메일', validators=[DataRequired('이메일을 입력해주세요'), Email()],
                       render_kw={'id': 'email', 'placeholder': '이메일'})
    submit = SubmitField('아이디 찾기')

# ---------------- Find Password ----------------
class FindPasswordForm(FlaskForm):
    email = EmailField(
        '가입한 이메일 주소',
        validators=[DataRequired('이메일을 입력해주세요'),
                    Email(message='올바른 이메일 형식이 아닙니다.')],
        render_kw={'id': 'email', 'class': 'form-control', 'placeholder': 'example@email.com'}
    )
    submit = SubmitField('비밀번호 재설정 링크 받기', render_kw={'class': 'btn btn-primary w-100'})

# ---------------- Login ----------------
class LoginForm(FlaskForm):
    userid = StringField(
        '아이디',
        validators=[DataRequired('아이디를 입력해주세요'),
                    Regexp(_USERID_RE, message='아이디는 영문/숫자/밑줄 6~20자여야 합니다.')],
        render_kw={'id': 'userid', 'class': 'form-control', 'placeholder': '아이디'}
    )
    password = PasswordField(
        '비밀번호',
        validators=[DataRequired('비밀번호를 입력해주세요')],
        render_kw={'id': 'password', 'class': 'form-control', 'placeholder': '비밀번호'}
    )
    submit = SubmitField('로그인', render_kw={'class': 'btn btn-primary'})


# ---------------- My page: change password ----------------
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        '현재 비밀번호',
        validators=[DataRequired('현재 비밀번호를 입력하세요')],
        render_kw={'id': 'current_password', 'class': 'form-control', 'autocomplete': 'current-password'}
    )
    new_password = PasswordField(
        '새 비밀번호',
        validators=[DataRequired('새 비밀번호를 입력하세요'),
                    Regexp(_PASSWORD_RE, message='영문, 숫자, 특수문자 포함 8~20자')],
        render_kw={'id': 'new_password', 'class': 'form-control', 'autocomplete': 'new-password'}
    )
    confirm_password = PasswordField(
        '비밀번호 확인',
        validators=[DataRequired('비밀번호 확인을 입력하세요'),
                    EqualTo('new_password', message='새 비밀번호가 일치하지 않습니다.')],
        render_kw={'id': 'confirm_password', 'class': 'form-control', 'autocomplete': 'new-password'}
    )
    submit = SubmitField('변경하기', render_kw={'class': 'btn btn-primary'})

    # 템플릿/기존 코드 호환: camelCase 별칭 제공
    @property
    def currentPassword(self):  # noqa: N802
        return self.current_password
    @property
    def newPassword(self):      # noqa: N802
        return self.new_password
    @property
    def confirmPassword(self):  # noqa: N802
        return self.confirm_password

    def validate(self, extra_validators=None):
        ok = super().validate(extra_validators=extra_validators)
        if not ok:
            return False
        if self.current_password.data == self.new_password.data:
            raise ValidationError('새 비밀번호가 현재 비밀번호와 같습니다.')
        return True

# ---------------- Reset Password ----------------
class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        '새 비밀번호',
        validators=[DataRequired(), Regexp(_PASSWORD_RE, message='영문, 숫자, 특수문자 포함 8~20자')],
        render_kw={'id': 'password', 'class': 'form-control'}
    )
    confirm_password = PasswordField(
        '비밀번호 확인',
        validators=[DataRequired(), EqualTo('password', message='비밀번호가 일치하지 않습니다.')],
        render_kw={'id': 'confirm_password', 'class': 'form-control'}
    )
    submit = SubmitField('비밀번호 변경하기', render_kw={'class': 'btn btn-primary w-100'})

# ---------------- Optional legacy forms ----------------
class UserLoginForm(FlaskForm):
    userid = StringField('userid', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('password', validators=[DataRequired()])

class UserSignupForm(FlaskForm):
    username = StringField('사용자이름', validators=[DataRequired()])
    userid = StringField('아이디', validators=[DataRequired(), Length(min=3, max=20)])
    password1 = PasswordField('비밀번호', validators=[DataRequired()])
    password2 = PasswordField('비밀번호확인', validators=[DataRequired(), EqualTo('password1', message='비밀번호가 일치하지 않습니다')])
    email = StringField('email', validators=[DataRequired(), Email()])

# ---------------- Store ----------------
class StoreForm(FlaskForm):
    title = StringField('제목', validators=[DataRequired()])
    content = TextAreaField('내용', validators=[DataRequired()])
    price = IntegerField('가격', validators=[DataRequired()])
    image = FileField('이미지', validators=[FileAllowed(['jpg', 'jpeg', 'png'], '이미지 파일만 업로드 가능합니다.')])

