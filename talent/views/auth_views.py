from flask import request, flash, redirect, url_for, User, Flask
from datetime import datetime
from talent.models import User
from werkzeug.security import generate_password_hash
from talent import db
app = Flask(__name__)

@app.route("/signup", methods=["POST"])
def signup():
    year = request.form.get("birth_year")
    month = request.form.get("birth_month")
    day = request.form.get("birth_day")

    try:
        birthday = datetime(int(year), int(month), int(day))
    except (TypeError, ValueError):
        flash("생년월일이 유효하지 않습니다.", "danger")
        return redirect(url_for("signup"))

    password = request.form.get("password")
    if not password:
        flash("비밀번호를 입력해주세요.", "danger")
        return redirect(url_for("signup"))
    hashed_password = generate_password_hash(password)

    new_user = User(
        userid=request.form["id"],
        password=hashed_password,
        email=request.form["email"] + "@naver.com",  # 도메인 처리 필요
        birthday=birthday,
        tel_number=request.form["tel_number"]
    )

    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for("login"))