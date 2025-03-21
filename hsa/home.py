from flask import Blueprint, render_template

# check for other template blueprint that might be needed
# e.g see blow for that of auth

# from flask import Blueprint
# from flask import flash
# from flask import g
# from flask import redirect
# from flask import render_template
# from flask import request
# from flask import session
# from flask import url_for
# from werkzeug.security import check_password_hash
# from werkzeug.security import generate_password_hash

bp = Blueprint("home", __name__,url_prefix="/home")

@bp.route("/")
def index():
    return render_template("home/index.html")