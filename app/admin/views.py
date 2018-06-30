from datetime import date

from flask import (abort, flash, redirect, render_template, request, session,
                   url_for)
from flask_login import current_user, login_required
from flask_paginate import Pagination

from . import admin
from .. import db
from ..decorators import superuser_check
from ..models import Category, Comment, Log, Post, User
from .forms import (CategoryAddForm, CategoryProfileEditForm,
                    DeleteCategoryForm, DeleteCommentForm, DeletePostForm,
                    DeleteUserForm, PostForm, SuperUserProfileEditForm,
                    UserAddForm, UserPasswordChangeForm, UserProfileEditForm)


@admin.route('/admin/index', methods=['GET', 'POST'])
@admin.route('/admin', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('admin/index.html', current_user=current_user)


@admin.route('/admin/post/list', methods=['GET', 'POST'])
@login_required
def post_list():
    page = request.args.get('page', 1, type=int)
    form2 = DeletePostForm()
    posts = Post.query.order_by(Post.id.desc())

    if current_user.is_superuser == False:
        posts = posts.filter(Post.author_id == current_user.id)

    pagination = posts.paginate(
        page, per_page=5, error_out=False)
    posts_items = pagination.items
    return render_template(
        'admin/post/list.html',
        posts=posts_items,
        pagination=pagination,
        form2=form2, current_user=current_user)


@admin.route('/admin/post/view/<int:id>', methods=['GET', 'POST'])
@login_required
def post_view_by_id(id):
    return redirect(url_for('main.post_view_by_id', id=id))


@admin.route('/admin/post/edit/add', methods=['GET', 'POST'])
@login_required
def post_add():
    form = PostForm()

    if form.validate_on_submit():

        post = Post(
            title=form.title.data,
            content=form.content.data,
            description=form.description.data,
            category_id=form.categories.data[0],
            update_time=date.today(),
            author_id=current_user.id,
            author_name=current_user.username)
        print(post.update_time)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('admin.post_list'))
    return render_template('admin/post/add.html', form=form, current_user=current_user)


@admin.route('/admin/post/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def post_edit(id):

    post = Post.query.get_or_404(id)
    category = Category.query.get_or_404(post.category_id)

    form = PostForm()
    if current_user.id == post.author_id and form.validate_on_submit():
        print(form.categories.data )
        print(category.id)
        post.title = form.title.data
        post.content = form.content.data
        post.description = form.description.data
        post.category_id = form.categories.data[0] if form.categories.data else category.id 
        post.update_time = date.today()
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.post_view_by_id', id=post.id))


    form.title.data = post.title
    form.description.data = post.description
    form.content.data = post.content
    # form.categories.data = category.id
    return render_template('admin/post/edit.html', form=form, post=post, current_user=current_user)


@admin.route('/admin/post/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def post_delete(id):
    form = DeletePostForm()
    if form.validate_on_submit():
        post_id = int(form.post_id.data)
        post = Post.query.get_or_404(post_id)
        if current_user.id == post.author_id or current_user.is_superuser == True:
            comments = Comment.query.filter(Comment.post_id == post_id).all()
            for comment in comments:
                db.session.delete(comment)
            db.session.delete(post)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                flash(u'删除失败！', 'danger')
            else:
                flash(u'成功删除文章', 'success')
    if form.errors:
        flash(u'删除失败！', 'danger')

    return redirect(url_for('admin.post_list'))


@admin.route('/admin/comment/list', methods=['GET', 'POST'])
@login_required
def comment_list():
    page = request.args.get('page', 1, type=int)
    form2 = DeleteCommentForm()
    comments = Comment.query.order_by(Comment.id.desc())
    query = db.session.query(Comment, Post)
    if current_user.is_superuser == False:
        comments = query.filter(Post.id == Comment.post_id).filter(
            Post.author_id == current_user.id)
        pagination = comments.paginate(
            page, per_page=5, error_out=False)
    else:
        comments = query.filter(Post.id == Comment.post_id)
        pagination = comments.paginate(
            page, per_page=5, error_out=False)

    comment_items = pagination.items

    return render_template(
        'admin/comment/list.html',
        comments=comment_items,
        pagination=pagination,
        form2=form2, current_user=current_user)


@admin.route('/admin/comment/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def comment_delete(id):
    form = DeleteCommentForm()

    if form.validate_on_submit():
        comment_id = int(form.comment_id.data)
        comment = Comment.query.get_or_404(comment_id)
        if current_user.is_superuser == False:
            post = Post.query.get_or_404(comment.post_id)
            if post.author_id != current_user.id:
                abort(404)

        db.session.delete(comment)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            flash(u'删除失败！', 'danger')
        else:
            flash(u'成功删除评论', 'success')
    if form.errors:
        flash(u'删除失败！', 'danger')

    return redirect(url_for('admin.comment_list'))


@admin.route('/admin/comment/moderate', methods=['GET', 'POST'])
@login_required
def comment_moderate():
    page = request.args.get('page', 1, type=int)

    query = db.session.query(Comment, Post)
    if current_user.is_superuser == False:
        comments = query.filter(Post.id == Comment.post_id).filter(
            Post.author_id == current_user.id)
        pagination = comments.paginate(
            page, per_page=5, error_out=False)
    else:
        comments = query.filter(Post.id == Comment.post_id)
        pagination = comments.paginate(
            page, per_page=5, error_out=False)

    comment_items = pagination.items
    return render_template('admin/comment/moderate.html',
                           comments=comments, pagination=pagination, page=page, current_user=current_user)


@admin.route('/admin/comment/<status>/<int:id>')
@login_required
def moderate_status(status, id):
    comment = Comment.query.get_or_404(id)
    if current_user.is_superuser == False:
        post = Post.query.get_or_404(comment.post_id)
        if post.author_id != current_user.id:
            abort(404)

    comment.disabled = False if status == 'enable' else True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('admin.comment_moderate', page=request.args.get('page', 1, type=int)))


@admin.route('/admin/user/list', methods=['GET', 'POST'])
@login_required
@superuser_check(current_user)
def user_list():
    page = request.args.get('page', 1, type=int)
    form2 = DeleteUserForm()
    pagination = User.query.order_by(User.id.desc()).paginate(
        page, per_page=5, error_out=False)
    users = pagination.items
    print(users[0].is_superuser)
    return render_template(
        'admin/user/list.html',
        users=users,
        pagination=pagination,
        form2=form2, current_user=current_user)


@admin.route('/admin/user/add', methods=['GET', 'POST'])
@login_required
@superuser_check(current_user)
def user_add():
    form = UserAddForm()

    if form.validate_on_submit():
        print('ddddd' + form.is_superuser.data)
        if form.first_password.data == form.second_password.data:
            is_superuser = False if form.is_superuser.data == 'N' else True
            User.insert_user(
                username=form.username.data,
                email=form.email.data,
                password=form.first_password.data,
                is_superuser=is_superuser
            )
            flash(u'成功增加管理员', 'success')
            return redirect(url_for('admin.user_list'))
        else:
            flash(u'两次密码输入不一致', 'failed')
            return redirect(url_for('admin.user_list'))
    return render_template('admin/user/add.html', form=form, current_user=current_user)


@admin.route('/admin/user/delete/<int:id>', methods=['GET', 'POST'])
@login_required
@superuser_check(current_user)
def user_delete(id):

    form = DeleteUserForm()
    if form.validate_on_submit():
        user_id = int(form.user_id.data)
        posts = Post.query.filter(Post.author_id == user_id).all()
        for post in posts:
            comments = Comment.query.filter(Comment.post_id == post.id).all()
            for comment in comments:
                db.session.delete(comment)
            db.session.delete(post)
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            flash(u'删除失败！', 'danger')
        else:
            flash(u'成功删除用户', 'success')
    if form.errors:
        flash(u'删除失败！', 'danger')
    return redirect(url_for('admin.user_list'))


@admin.route('/admin/user/edit/profile/<int:id>', methods=['GET', 'POST'])
@login_required
def user_edit_profile(id):
    if current_user.id == id or current_user.is_superuser == True:
        user = User.query.get_or_404(id)
        form = SuperUserProfileEditForm(
        ) if current_user.is_superuser == True else UserProfileEditForm()
        if form.validate_on_submit():
            user.username = form.username.data
            user.email = form.email.data
            if current_user.is_superuser == True:
                user.is_superuser = False if form.is_superuser.data == 'N' else True
            db.session.add(user)
            db.session.commit()
            flash(u'资料修改成功', 'success')
            return redirect(url_for('admin.user_list')) if current_user.is_superuser == True else redirect(url_for('admin.index'))

        form.username.data = user.username
        form.email.data = user.email
        form.is_superuser.data = 'Y' if user.is_superuser == True else 'N'
        return render_template('admin/user/profile.html', form=form, user=user, current_user=current_user)
    else:
        abort(404)


@admin.route('/admin/user/edit/password/<int:id>', methods=['GET', 'POST'])
@login_required
def user_edit_password(id):
    if current_user.id == id or current_user.is_superuser == True:
        user = User.query.get_or_404(id)
        form = UserPasswordChangeForm()
        if form.validate_on_submit() and form.first_new_password.data == form.second_new_password.data:
            if user.verify_password(form.old_password.data):
                print(form.second_new_password.data)
                user.password = form.first_new_password.data
                db.session.add(user)
                db.session.commit()
                flash(u'资料修改成功', 'success')
                return redirect(url_for('admin.user_list')) if current_user.is_superuser == True else redirect(url_for('admin.index'))
        return render_template('admin/user/password.html', form=form, user=user, current_user=current_user)
    else:
        abort(404)


@admin.route('/admin/category/list', methods=['GET', 'POST'])
@login_required
def category_list():
    page = request.args.get('page', 1, type=int)
    form3 = DeleteCategoryForm()
    pagination = Category.query.order_by(Category.id.desc()).paginate(
        page, per_page=5, error_out=False)
    categories = pagination.items
    return render_template(
        'admin/category/list.html',
        categories=categories,
        pagination=pagination,
        form3=form3, current_user=current_user)


@admin.route('/admin/category/add', methods=['GET', 'POST'])
@login_required
def category_add():
    form = CategoryAddForm()
    if form.validate_on_submit():
        Category.insert_cate(name=form.name.data,
                             author_id=current_user.id,
                             author_name=current_user.username)
        flash(u'成功添加类别', 'success')
        return redirect(url_for('admin.category_list'))
    return render_template('admin/category/add.html', form=form, current_user=current_user)


@admin.route('/admin/category/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def category_delete(id):
    form = DeleteCategoryForm()
    if form.validate_on_submit():
        category_id = int(form.category_id.data)
        print(category_id)
        category = Category.query.get_or_404(category_id)
        db.session.delete(category)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            flash(u'删除失败！', 'danger')
        else:
            flash(u'成功删除类别', 'success')
    if form.errors:
        flash(u'删除失败！', 'danger')
    return redirect(url_for('admin.category_list'))


@admin.route('/admin/category/edit/profile/<int:id>', methods=['GET', 'POST'])
@login_required
def category_edit_profile(id):
    if current_user.id == id or current_user.is_superuser == True:
        category = Category.query.get_or_404(id)
        form = CategoryProfileEditForm()
        if form.validate_on_submit():
            category.name = form.name.data
            db.session.add(category)
            db.session.commit()
            return redirect(url_for('admin.category_list'))

        form.name.data = category.name

        return render_template('admin/category/profile.html', form=form, category=category, current_user=current_user)
    else:
        return abort(404)


@admin.route('/admin/log', methods=['GET', 'POST'])
@login_required
@superuser_check(current_user)
def log():
    page = request.args.get('page', 1, type=int)
    pagination = Log.query.order_by(Log.id.desc()).paginate(
        page, per_page=5, error_out=False)
    logs = pagination.items
    return render_template(
        'admin/log/list.html',
        logs=logs,
        pagination=pagination, current_user=current_user
    )
