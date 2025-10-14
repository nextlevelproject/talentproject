# talent/forms.py
import datetime as dt
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import (
    StringField, PasswordField, SelectField, SubmitField, BooleanField,
    TextAreaField, FileField, IntegerField, SelectMultipleField, widgets
)
from wtforms.fields import EmailField
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
        render_kw={'id': 'current_password', 'class': 'form-control'}
    )
    new_password = PasswordField(
        '새 비밀번호',
        validators=[DataRequired('새 비밀번호를 입력하세요'),
                    Regexp(_PASSWORD_RE, message='영문, 숫자, 특수문자 포함 8~20자')],
        render_kw={'id': 'new_password', 'class': 'form-control'}
    )
    confirm_password = PasswordField(
        '비밀번호 확인',
        validators=[DataRequired('비밀번호 확인을 입력하세요'),
                    EqualTo('new_password', message='새 비밀번호가 일치하지 않습니다.')],
        render_kw={'id': 'confirm_password', 'class': 'form-control'}
    )
    submit = SubmitField('변경하기', render_kw={'class': 'btn btn-primary'})

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

# ---------------- Category ----------------
class MultiCheckboxField (SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class MoveForm(FlaskForm):
    move = MultiCheckboxField(
        '이사', choices=[
            ('one_room', '원룸/소형이사'),('two_rooms', '가정이사(투룸이상)'),
            ('m_office', '사무실/상업공간이사'),('freight', '화물이사')])
    remove = MultiCheckboxField(
        '철거', choices=[('remove', '철거'),('waste', '폐기')])

class CleaningForm(FlaskForm):
    house_clean = MultiCheckboxField(
        '청소', choices=[
            ('move_in_clean', '입주청소'),('remove_mold', '곰팡이 제거'),
            ('nano_coating', '나노코팅 시공'),('insulation', '단열/결로 시공'),
            ('c_boiler', '보일러/배관 청소'), ('line', '줄눈 시공'),
            ('calking', '코킹 시공'),('drain', '하수구 청소')])
    furniture_clean = MultiCheckboxField(
        '가구청소', choices=[
            ('c_refrigerator', '냉장고 청소'), ('c_washer', '세탁기 청소'),
            ('sofa', '소파 청소'), ('c_air_conditioner', '에어컨 청소'),
            ('c_hood', '후드 청소'),('bed', '침대 / 매트리스 청소')])
    office_clean = MultiCheckboxField(
        '사업장청소', choices=[
            ('inside', '건물내부 청소'),('outside', '건물외부 청소'),
            ('stairs', '계단/화장실 청소'),('ventilation', '환풍구 청소'),
            ('floor', '바닥 청소'),('c_carpet', '카페트 청소')])
    distinct_clean = MultiCheckboxField(
        '특수 청소', choices=[
            ('organization_wash', '단체 세탁'), ('cockroach', '바퀴벌레 퇴치'),
            ('water_tank', '물탱크 청소'), ('fumigator', '방역소독'),
            ('stink', '악취 제거'),('relics', '유품정리 / 특수청소'),
            ('flooding', '침수 복구 및 청소'),('fire', '화재 복구 및 청소')])

class InstallForm(FlaskForm):
    install = MultiCheckboxField(
        '설치', choices=[
            ('CCTV','CCTV 설치'),('loT','loT 설치'), ('i_kitchen_system', '주방가구 설치'),
            ('i_door','문 / 창문 설치'), ('i_doorlock', '열쇠 / 도어락 설치'),
            ('electronic', '전기 / 태양광패널 설치'), ('i_boiler', '보일러 설치'),
            ('internet', '인터넷 / 랜 공사'), ('i_furniture', '가구 설치'),
            ('i_etc', '기타 설치')])

class RepairForm(FlaskForm):
    repair = MultiCheckboxField(
        '수리', choices=[
            ('r_kitchen_system', '주방가구 수리'),('electronic_device', '전자제품 수리'),
            ('computer', '컴퓨터 수리'), ('r_doorlock', '도어락 수리'),
            ('r_boiler', '보일러 수리'), ('r_furniture', '가구 수리'),
            ('r_etc', '기타 수리')])

class InteriorForm(FlaskForm):
    overall = MultiCheckboxField(
        '종합', choices=[
            ('house', '집 인테리어'), ('apart', '아파트 인테리어'),
            ('o_office', '상업공간 인테리어')])
    part = MultiCheckboxField(
        '부분', choices=[
            ('p_furniture', '가구 리품'), ('lighting', '조명 인테리어'),
            ('toilet', '화장실 리모델링'), ('p_kitchen', '주방 리모델링')])
    wall = MultiCheckboxField(
        '벽, 바닥', choices=[
            ('fake_wall', '가벽'), ('film', '필름 시공'),
            ('paint', '페인트 시공'), ('maru', '마루 시공'),
            ('linoleum', '장판 시공'), ('w_carpet', '카페트 시공'),
            ('tile', '타일 시공')])
    outside = MultiCheckboxField(
        '야외', choices=[
            ('sign','간판 제작'),('pool', '수영장 / 스파 시공'),
            ('rooptop', '옥상 시공'), ('outwall', '외벽 리모델링')])

class EventForm(FlaskForm):
    wedding = MultiCheckboxField(
        '웨딩', choices=[
            ('host', '사회자'), ('dress', '맞춤정장'),
            ('wd_sdm', '스드메 / 웨딩플래너'), ('song', '축가')])
    shooting = MultiCheckboxField(
        '촬영', choices=[
            ('photo_s', '사진 촬영'), ('video_s', '영상 촬영'),
            ('drawn', '드론 촬영'), ('streaming', '생중계 / 스트리밍 촬영'),
            ('snap', '스냅촬영'), ('video_edit', '영상 편집'), ('caption', '자막 제작')])
    rental = MultiCheckboxField(
        '대여', choices=[
            ('instrument', '악기 대여'), ('clothes', '의상 대여'),
            ('camera', '카메라 대여'), ('bus', '버스 대여'),
            ('cinema', '극장대관'), ('studio', '스튜디오대관'),
            ('practice', '연습실 대관')])
    event = MultiCheckboxField(
        '행사', choices=[
            ('pro_item', '굿즈 / 판촉물 제작'), ('postcard', '장식 / 엽서 제작'),
            ('booth', '부스 제작'), ('plan', '행사기획'), ('performance', '공연 섭외'),
            ('guard', '경호원'), ('guide', '행사 도우미'), ('MC', '행사 MC')])

class BeautyForm(FlaskForm):
    beauty = MultiCheckboxField(
        '뷰티', choices=[
            ('nail', '네일'), ('scalp', '두피 / 모발 관리'), ('eyebrow', '눈썹 / 속눈썹'),
            ('waxing', '왁싱'), ('personal_color', '퍼스널 컬러 / 이미지 메이킹'),
            ('skin', '피부 관리'), ('hair', '헤어 / 메이크업')])

class FashionForm(FlaskForm):
    fashion = MultiCheckboxField(
        '패션', choices=[
            ('group_shirt', '단체복 제작'), ('group_clothes', '맞춤옷 제작'),('mending','명품 수선 / 리폼'),
            ('handmade', '수제화 제작')])

class EmployForm(FlaskForm):
    employment = MultiCheckboxField(
        '취업', choices=[
            ('interview', '면접 컨설팅'), ('speech', '스피치 컨설팅'),('crewman', '승무원 준비'),
            ('employment', '취업 컨설팅'), ('resume', '이력서 / 자소서'), ('written', '인적성 / 필기시험'),
            ('portfolio', '포트폴리오 컨설팅'), ('foreign', '해외취업 컨설팅')])

class PriForm(FlaskForm):
    lesson = MultiCheckboxField(
        '과외', choices=[
            ('private_lesson', '검정고시/국어'), ('thesis_consulting', '논문 컨설팅'),
            ('debate_lesson', '토론 과외'), ('quick_reading_lesson', '속독 과외'),
            ('math_lesson', '수학 과외'), ('english_lesson', '영어 과외'),
            ('social_lesson', '사회 과외'), ('an-essay_lesson', '속독 과외')])
    music = MultiCheckboxField(
        '음악', choices=[('vocal', '보컬 레슨'), ('voice_actor', '성우 레슨'),
            ('acting_lesson', '연기 레슨'), ('musical_lesson', '뮤지컬 레슨'),
            ('djing_lesson', '디제잉 레슨'), ('violin_lesson', '바이올린 레슨')])

    dance = MultiCheckboxField(
        '댄스', choices=[('broadcast', '방송 댄스'), ('ballet', '발레 레슨'),
                       ('pole_dance', '폴댄스 레슨'), ('korean_dance', '한국무용 레슨'),
                       ('hula_dance', '훌라댄스 레슨'), ('tap_dance', '탭댄스 레슨')])

class HobbyForm(FlaskForm):
    hobby = MultiCheckboxField(
        '취미', choices=[
            ('boxing_lesson', '복싱 레슨'), ('judo', '유도 레슨'),
            ('mixed_maritial_arts_lesson', '종합격투기 레슨'), ('taekwondo_lesson', '태권도 레슨'),
            ('double-headed_lesson', '쌍절곤 레슨'), ('hapkido_lesson', '합기도 레슨'),
            ('defence_lesson', '호신술 레슨'), ('fencing_lesson', '펜싱 레슨')])
    photo = MultiCheckboxField(
        '사진', choices=[('photography', '사진촬영 레슨'), ('video_recording', '영상촬영 레슨')])
    investment= MultiCheckboxField(
        '투자', choices=[('gift_lesson', '선물 레슨'), ('cryptocurrency_lesson', '암호화폐 레슨'),
                        ('stock_lesson', '주식 레슨'), ('blogger_lesson', '블로거 레슨'),
                        ('market_lesson', '오픈마켓 레슨'), ('purchasing-agent_lesson', '구매대행 레슨')])

class PetForm(FlaskForm):
    pet = MultiCheckboxField(
        '반려동물', choices=[
            ('walk', '반려견 산책'), ('p_beauty', '반려동물 미용'),
            ('feed', '수제 사료 / 간식'), ('funeral', '반려동물 장례'),
            ('training', '반려동물 훈련'), ('sitter', '펫 시터')])

class LawForm(FlaskForm):
    finance= MultiCheckboxField(
        '금융', choices=[
            ('insurance_disign', '보험설계'), ('traveler_insurance', '여행자보험'),
            ('pet_insurance', '펫 보험'), ('fire_insurance', '화재보험'),
            ('cancer_insurance', '암 보험'), ('issuance_card', '카드발급'),
            ('car_insurance', '자동차 보험'), ('traveler_insurance', '여행자보험')])
    law = MultiCheckboxField(
        '법률', choices=[('civil_action', '민사소송'), ('patent_application', '특허출원'),
                        ('damages', '손해배상'), ('fraud', '사기'),
                        ('criminal', '형사소송'), ('legal_docuents', '법률서류 작성'),
                        ('defamation', '명예훼손'), ('divorce', '이혼'),
                        ('revival', '회생'), ('embezzle', '횡령'),
                        ('lawsuit', '행정소송'), ('intellectual_property', '지식재산')])

class CarForm(FlaskForm):
    car_design = MultiCheckboxField(
        '차량관리', choices=[
            ('steam car_wash', '스팀 세차'), ('car_tinting', '자동차 썬팅'),
            ('automobile_tuning', '자동차 튜닝'), ('business trip_tax', '출장세차'),
            ('wrapping', '자동차 랩핑'), ('exterior_repair', '자동차 외부수리'),
            ('motorcycle_repair', '오토바이 수리'), ('black-box', '블랙박스 설치'),
            ('maintenance', '자동차 정비'), ('luster', '자동차광택')])
    car = MultiCheckboxField(
        '자동차매매', choices=[('car_puchase', '자동차 구매'), ('camping car_making', '캠핑카 제작'),
                             ('used_car', '중고차 판매'), ('lease', '자동차 리스'),
                             ('new_car', '신차 판매'), ('car_company', '자동차 구매동행')])

class TravelForm(FlaskForm):
    travel = MultiCheckboxField(
        '여행', choices=[
                ('domestic_traval', '국내 여행'), ('southern_europe', '남유럽 여행'),
                ('southeast_asia', '동남아 여행'), ('animal_trip', '반려동물 동반여행'),
                ('africa', '아프리카 여행'), ('japan', '일본 여행'),
                ('china', '중국 여행'), ('latin_america', '중남미 여행'),
                ('india', '인도 여행'), ('western_europe', '서유럽 여행'),
                ('hongkong', '홍콩 여행'), ('taiwan', '대만 여행'),
                ('singapore', '싱가폴 여행'), ('oceania', '오세아니아 여행')])

class EtcForm(FlaskForm):
    psycology = MultiCheckboxField(
        '심리상담', choices=[
            ('family', '가족 상담'), ('couple', '부부 / 커플 치료'), ('adult', '성인 상담'),
            ('psycology_s', '심리 검사'), ('art', '미술치료'), ('music', '음악치료'), ('movie', '영화 / 사진치료')])
    translation = MultiCheckboxField(
        '번역 / 통역', choices=[
            ('etc_t', '기타 번역 / 통역'), ('english', '영어 번역 / 통역'),
            ('chinese', '중국어 번역 / 통역'), ('japanese', '일본어 번역 / 통역'),
            ('Chinese_s', '한문 번역 / 통역'), ('german', '독일어 번역 / 통역'),
            ('sweden', '스웨덴어 번역 / 통역'), ('italy', '이탈리아어 번역 / 통역'),
            ('spain', '스페인어 번역 / 통역'), ('aran', '아랍어 번역 / 통역')])
    errand = MultiCheckboxField(
        '심부름 / 알바', choices=[
            ('accompany', '동행 심부름'), ('purchase', '물품 구매/배달'),
            ('role', '역할대행 심부름'), ('housework', '가사 도우미'),('serving', '서빙 / 주방 알바'),
            ('service', '서비스 / 행사 알바'), ('production', '생산 / 기능 / 노무 알바'),
            ('store_m', '매장관리 / 판매 알바'), ('office_job', '사무직 알바'), ('broadcasting', '방송 / 미디어 알바'),
            ('culture', '문화 / 여가 알바'), ('hospital', '병원 / 간호 알바'), ('etc_e', '기타 알바')])