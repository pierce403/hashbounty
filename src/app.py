import settings

from flask import Flask
app = Flask(__name__)

from flask import url_for, redirect, make_response, render_template, abort

@app.route('/')
def main():
    return render_template("construction.html")

