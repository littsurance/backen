from flask import Flask 


app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Hey There! {TEST}</h1>'


app.run()