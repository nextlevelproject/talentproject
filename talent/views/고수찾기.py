from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('고수찾기.html')

if __name__ == '__고수찾기__':
    app.run(debug=True)
