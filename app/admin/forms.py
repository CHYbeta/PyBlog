from flask_wtf import FlaskForm
from wtforms import (BooleanField, HiddenField, PasswordField, RadioField,
                     SelectMultipleField, StringField, TextAreaField)
from wtforms.validators import DataRequired, Email, length

from ..models import Category


class PostForm(FlaskForm):
    title = StringField('文章标题', validators=[DataRequired(), length(max=255)])
    description = StringField(
        '文章简介', validators=[DataRequired(), length(max=255)])
    content = TextAreaField('文章内容', validators=[DataRequired()])
    categories = SelectMultipleField('分类', coerce=int)

    def __init__(self):
        super(PostForm, self).__init__()
        self.categories.choices = [(c.id, c.name)
                                   for c in Category.query.order_by('id')]


class UserAddForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), length(max=64)])
    email = StringField(
        '邮箱', validators=[DataRequired(), Email(), length(max=64)])
    first_password = PasswordField(
        '请输入用户密码', validators=[DataRequired(), length(max=64)])
    second_password = PasswordField('请再次确认用户密码', validators=[
                                    DataRequired(), length(max=64)])
    is_superuser = RadioField('是否是超级管理员', choices=[('Y', 'Yes'), ('N', 'No')],
                              validators=[DataRequired()])


class SuperUserProfileEditForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), length(max=64)])
    email = StringField(
        '邮箱', validators=[DataRequired(), Email(), length(max=64)])
    is_superuser = RadioField('是否是超级管理员', choices=[('Y', 'Yes'), ('N', 'No')])


class UserProfileEditForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), length(max=64)])
    email = StringField(
        '邮箱', validators=[DataRequired(), Email(), length(max=64)])
    is_superuser = HiddenField('是否是超级管理员(不可修改): ')


class CategoryProfileEditForm(FlaskForm):
    name = StringField('新类名', validators=[DataRequired(), length(max=64)])


class UserPasswordChangeForm(FlaskForm):
    old_password = PasswordField('请输入旧的用户密码', validators=[
                                 DataRequired(), length(max=64)])
    first_new_password = PasswordField(
        '请输入新的用户密码', validators=[DataRequired(), length(max=64)])
    second_new_password = PasswordField('请再次确认新的用户密码', validators=[
                                        DataRequired(), length(max=64)])


class CategoryAddForm(FlaskForm):
    name = StringField('分类名', validators=[DataRequired(), length(max=64)])


class DeletePostForm(FlaskForm):
    post_id = StringField(validators=[DataRequired()])


class DeleteCommentForm(FlaskForm):
    comment_id = StringField(validators=[DataRequired()])


class DeleteUserForm(FlaskForm):
    user_id = StringField(validators=[DataRequired()])


class DeleteCategoryForm(FlaskForm):
    category_id = StringField(validators=[DataRequired()])
