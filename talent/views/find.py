from flask import Flask, render_template

bp = Flask(__name__)

@bp.route('/')
def home():
    return render_template('find.html')

if __name__ == '__find__':
    app.run(debug=True)
