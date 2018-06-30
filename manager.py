import os

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


@manager.command
def create_db():
    """Create database for """
    db.create_all()


@manager.option('-e', '--email', dest='email', default='admin@pyblog.com')
@manager.option('-u', '--username', dest='username', default='admin')
@manager.option('-p', '--password', dest='password', default='admin')
def create_user(email, username, password):
    User.insert_user(username=username, email=email,
                     password=password, is_superuser=True)


if __name__ == '__main__':
    manager.run()
