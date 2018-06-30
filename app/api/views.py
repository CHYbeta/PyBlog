from flask import jsonify
from flask_login import login_required

from . import api
from .. import db
from ..models import Category, Comment, Post, User


@api.route('/api/stats/summary', methods=['GET', 'POST'])
@login_required
def summary():
    info = dict()
    info['post_count'] = post_count(Post)
    info['comment_count'] = comment_count(Comment)
    info['category_count'] = category_count(Category)
    info['user_count'] = user_count(User)
    return jsonify(info)


def user_count(User):
    return db.session.query(User).count()


def post_count(Post):
    return db.session.query(Post).count()


def comment_count(Comment):
    return db.session.query(Comment).count()


def category_count(Category):
    return db.session.query(Category).count()
