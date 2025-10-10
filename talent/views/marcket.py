from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('마켓.html')

if __name__ == '__마켓__':
    app.run(debug=True)
