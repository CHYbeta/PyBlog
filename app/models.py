import hashlib
from datetime import date, datetime

from flask_login import UserMixin, current_user
from sqlalchemy import event
from werkzeug.security import check_password_hash, generate_password_hash

from . import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(64), unique=True, nullable=True, index=True)
    username = db.Column(db.String(64), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(128), nullable=True)
    last_login_at = db.Column(db.DateTime(), nullable=True)
    now_login_at = db.Column(db.DateTime(), nullable=True)
    last_login_ip = db.Column(db.String(100), nullable=True)
    now_login_ip = db.Column(db.String(100), nullable=True)
    is_superuser = db.Column(db.Boolean, nullable=True, default=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic',
                            cascade='all, delete-orphan')            # 一个用户有多条发表，一对多

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def insert_user(email, username, password, is_superuser):
        password_hash = generate_password_hash(password)
        user = User(email=email, username=username,
                    password_hash=password_hash)
        if is_superuser == True:
            user.is_superuser = True
        else:
            user.is_superuser = False
        db.session.add(user)
        db.session.commit()

    def __init__(self, email, username, password_hash):
        self.email = email
        self.username = username
        self.password_hash = password_hash


class Post(db.Model):

    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(64), unique=True, index=True)
    content = db.Column(db.Text)
    description = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author_name = db.Column(db.String(64), nullable=True, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    update_time = db.Column(db.Date, nullable=True, index=True)

    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @property
    def markdown2html(self):
        import markdown
        return markdown.markdown(self.content, ['extra', 'toc'])


class Category(db.Model):

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'))  # author's id of the category
    author_name = db.Column(db.String(64), nullable=True, index=True)
    name = db.Column(db.String(64), unique=True, index=True)
    count = db.Column(db.Integer)  # count how many posts in this category
    posts = db.relationship('Post', backref='category', lazy='dynamic')

    @staticmethod
    def insert_cate(name, author_id, author_name):
        category = Category(name=name, author_id=author_id,
                            author_name=author_name)
        db.session.add(category)
        db.session.commit()

    def __init__(self, name, author_id, author_name):
        self.name = name
        self.author_id = author_id
        self.author_name = author_name
        self.count = 0


class Comment(db.Model):

    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text)
    content_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    disabled = db.Column(db.Boolean, default=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    post_title = db.Column(db.String(64), nullable=True, index=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Log(db.Model):

    __tablename__ = 'logs'
#    __table_args__ = {
#        'mysql_charset' : "utf8"
#    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    opr_type = db.Column(db.String(64))
    opr_obj = db.Column(db.String(64))
    msg = db.Column(db.String(64))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author_name = db.Column(db.String(64), nullable=True, index=True)
    update_time = db.Column(db.DateTime(), nullable=True, index=True)


@event.listens_for(Category, 'after_insert')
def category_after_insert(mapper, connection, target):
    table = Log.__tablename__
    connection.execute(
        "insert into " + table +
        " (opr_type,opr_obj,msg,author_id,author_name,update_time) values (" +
        "'insert', 'category', '" + target.name
        + "', " + repr(current_user.id) + "," +
        repr(current_user.username) + ", '" + str(datetime.now()) + "');"
    )


@event.listens_for(Category, 'after_delete')
def category_after_delete(mapper, connection, target):
    table = Log.__tablename__
    connection.execute(
        "insert into " + table +
        " (opr_type,opr_obj,msg,author_id,author_name,update_time) values (" +
        "'delete', 'category', '" + target.name
        + "', " + repr(current_user.id) + "," +
        repr(current_user.username) + ", '" + str(datetime.now()) + "');"
    )


@event.listens_for(Category, 'after_update')
def category_after_update(mapper, connection, target):
    table = Log.__tablename__
    connection.execute(
        "insert into " + table +
        " (opr_type,opr_obj,msg,author_id,author_name,update_time) values (" +
        "'update', 'category', '" + target.name
        + "', " + repr(current_user.id) + "," +
        repr(current_user.username) + ", '" + str(datetime.now()) + "');"
    )


@event.listens_for(User, 'after_insert')
def user_after_insert(mapper, connection, target):
    table = Log.__tablename__
    try:
        connection.execute(
            "insert into " + table +
            " (opr_type,opr_obj,msg,author_id,author_name,update_time) values (" +
            "'insert', 'user', '" + target.username
            + "', " + repr(current_user.id) + "," +
            repr(current_user.username) + ", '" + str(datetime.now()) + "');"
        )
    except AttributeError:
        pass


@event.listens_for(User, 'after_delete')
def user_after_delete(mapper, connection, target):
    table = Log.__tablename__
    connection.execute(
        "insert into " + table +
        " (opr_type,opr_obj,msg,author_id,author_name,update_time) values (" +
        "'delete', 'user', '" + target.username
        + "', " + repr(current_user.id) + "," +
        repr(current_user.username) + ", '" + str(datetime.now()) + "');"
    )


@event.listens_for(User, 'after_update')
def user_after_update(mapper, connection, target):
    table = Log.__tablename__
    connection.execute(
        "insert into " + table +
        " (opr_type,opr_obj,msg,author_id,author_name,update_time) values (" +
        "'update', 'category', '" + target.username
        + "', " + repr(current_user.id) + "," +
        repr(current_user.username) + ", '" + str(datetime.now()) + "');"
    )


@event.listens_for(Post, 'after_insert')
def post_after_insert(mapper, connection, target):
    table = Log.__tablename__
    connection.execute(
        "insert into " + table +
        " (opr_type,opr_obj,msg,author_id,author_name,update_time) values (" +
        "'insert', 'post', '" + target.title
        + "', " + repr(current_user.id) + "," +
        repr(current_user.username) + ", '" + str(datetime.now()) + "');"
    )


@event.listens_for(Post, 'after_delete')
def post_after_delete(mapper, connection, target):
    table = Log.__tablename__
    connection.execute(
        "insert into " + table +
        " (opr_type,opr_obj,msg,author_id,author_name,update_time) values (" +
        "'delete', 'post', '" + target.title
        + "', " + repr(current_user.id) + "," +
        repr(current_user.username) + ", '" + str(datetime.now()) + "');"
    )


@event.listens_for(Post, 'after_update')
def post_after_update(mapper, connection, target):
    table = Log.__tablename__
    connection.execute(
        "insert into " + table +
        " (opr_type,opr_obj,msg,author_id,author_name,update_time) values (" +
        "'update', 'post', '" + target.title
        + "', " + repr(current_user.id) + "," +
        repr(current_user.username) + ", '" + str(datetime.now()) + "');"
    )
