from flask import Blueprint, render_template

viwes = Blueprint(__name__, "viwes")

@viwes.route('/')
def home():
    return render_template('index.html')