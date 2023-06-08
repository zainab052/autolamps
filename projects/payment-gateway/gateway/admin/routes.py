from flask import Blueprint, request, json, \
    current_app, render_template, redirect
from gateway.models import Setup
from gateway import db

mod = Blueprint('admin', __name__, url_prefix='/admin')


@mod.route('/')
def login():
    return render_template('login.html')


@mod.route('/handle_data', methods=["GET", "POST"])
def handle_data():
    if request.method == "POST":
        req = request.form
        print(req)
        return redirect(request.url)
    setup = Setup.query.get(1)
    return render_template("settings.html", setup=setup)
    # your code
    # return a response


@mod.route('/seturl', methods=["GET", "POST"])
def seturl():
    url = request.form['url']
    setup = Setup.query.get(1)
    print("db", setup)
    if setup is None:
        calback_url = Setup(url=url)
        db.session.add(calback_url)
        db.session.commit()
    else:
        setup.url = url
        db.session.add(setup)
        db.session.commit()
    return render_template("settings.html", setup=setup)


@mod.route('/dash',methods=['GET'])
def show_dah():
    return render_template('Dashboard.html')