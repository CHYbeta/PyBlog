from flask import redirect, render_template, request, session, url_for
from flask_login import current_user
from flask_paginate import Pagination

from app.models import Category, Comment, Post

from . import main
from .. import db
from .forms import CommentForm, NameForm


@main.route('/', methods=['GET', 'POST'])
@main.route('/index', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    # pagination = Post.query.join(Category).order_by(Post.id.desc()).paginate(
    #    page, per_page=2, error_out=False)
    pagination = db.session.query(Post, Category.name).filter(Post.category_id == Category.id).order_by(Post.id.desc()).paginate(
        page, per_page=5, error_out=False)
    posts = pagination.items
    return render_template(
        'index.html',
        posts=posts,
        pagination=pagination)


@main.route('/posts', methods=['GET', 'POST'])
def view_posts():
    page = request.args.get('page', 1, type=int)
    result = Post.query.order_by(Post.update_time.desc())
    pagination = result.paginate(
        page, per_page=5, error_out=False)
    posts = pagination.items
    lenght = len(result.all())
    return render_template(
        'posts.html',
        posts=posts, lenght=lenght,
        pagination=pagination)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post_view_by_id(id):
    post = Post.query.get_or_404(id)
    category = Category.query.get_or_404(post.category_id)
    category = category.name
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data,
                          post=post,
                          post_id=post.id,
                          post_title=post.title
                          )
        db.session.add(comment)
        db.session.commit()

        return redirect(url_for('main.post_view_by_id', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count()-1)//10 + 1

    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=10, error_out=False
    )
    comments = pagination.items
    return render_template('postview.html', post=post, form=form, category=category,
                           comments=comments, pagination=pagination)


@main.route('/categories', methods=['GET', 'POST'])
def view_by_categories():
    page = request.args.get('page', 1, type=int)
    result = Category.query.order_by(Category.id.desc())
    pagination = result.paginate(
        page, per_page=5, error_out=False)
    categories = pagination.items
    return render_template(
        'categories.html',
        categories=categories,
        pagination=pagination)


@main.route('/about', methods=['GET', 'POST'])
def about_the_site():
    return "hacked by chybeta"


@main.route('/category/<int:cid>', methods=['GET', 'POST'])
def post_view_by_category(cid):
    page = request.args.get('page', 1, type=int)
    result = Post.query.filter(Post.category_id == cid).order_by(
        Post.update_time.desc())
    pagination = result.paginate(
        page, per_page=5, error_out=False)
    posts = pagination.items
    lenght = len(result.all())
    return render_template(
        'posts.html',
        posts=posts, lenght=lenght,
        pagination=pagination)
