from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('submit')


class CommentForm(FlaskForm):
    content = PageDownField(label=u'发表评论', validators=[Required()])
    submit = SubmitField(label=u'提交')
