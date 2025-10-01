from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.fields.simple import StringField, TextAreaField, FileField
from wtforms.validators import DataRequired

# STORE
class StoreForm(FlaskForm):
    title = StringField('제목', validators=[DataRequired('제목은 필수입력 항목입니다.')])
    content = TextAreaField('내용',validators=[DataRequired('내용은 필수입력 항목입니다.')])
    image = FileField('이미지', validators=[FileRequired(),FileAllowed(['jpg', 'jpeg', 'png'], '이미지 파일만 업로드 가능합니다.')])