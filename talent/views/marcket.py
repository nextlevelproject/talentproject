from flask import Flask, render_template

bf = Flask(__name__)

@bf.route('/')
def home():
    return render_template('market.html')

if __name__ == '__market__':
    app.run(debug=True)
