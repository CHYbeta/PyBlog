from datetime import datetime

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from . import auth
from .. import db
from ..models import User
from .forms import LoginForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            current_user.now_login_at = str(datetime.now())
            current_user.now_login_ip = request.remote_addr or None
            db.session.add(current_user)
            db.session.commit()
            flash(u'%s 登陆成功!' % user.username)
            return redirect(request.args.get('next') or url_for('admin.index'))
        else:
            flash(u'登陆失败！用户名或密码错误，请重新登陆。', 'danger')
    if form.errors:
        flash(u'登陆失败，请尝试重新登陆.', 'danger')

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    print(current_user.now_login_at)
    current_user.last_login_at = current_user.now_login_at
    current_user.last_login_ip = current_user.now_login_ip
    db.session.add(current_user)
    db.session.commit()
    logout_user()
    flash(u'您已退出登陆。', 'success')
    return redirect(url_for('main.index'))
