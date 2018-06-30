from flask import Blueprint, Flask, render_template
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flaskext.markdown import Markdown

from config import config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
bootstrap = Bootstrap()
csrf = CSRFProtect()
main = Blueprint('main', __name__)
moment = Moment()

global_curYear = 2018
global_curMonth = 6
global_left = True


def get_curYear():
    return global_curYear


def set_curYear(var):
    global global_curYear
    global_curYear = var
    return ""


def get_curMonth():
    return global_curMonth


def set_curMonth(var):
    global global_curMonth
    global_curMonth = var
    return ""


def get_left():
    return global_left


def set_left(var):
    global global_left
    global_left = var
    return ""


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    Markdown(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint)
    app.add_template_global(get_curYear, 'get_curYear')
    app.add_template_global(set_curYear, 'set_curYear')
    app.add_template_global(get_curMonth, 'get_curMonth')
    app.add_template_global(set_curMonth, 'set_curMonth')
    app.add_template_global(get_left, 'get_left')
    app.add_template_global(set_left, 'set_left')

    return app
