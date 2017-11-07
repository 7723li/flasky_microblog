#!/usr/bin/env python
import os, sys
from app import create_app, db
from app.models import User, Role, Post, Follow
from app.main.forms import photos
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
import flask_whooshalchemy as whooshalchemy

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)
configure_uploads(app,photos)
patch_request_class(app)
whooshalchemy.whoosh_index(app, Post)

def make_shell_context():#context 语境;上下文;背景;环境
    return dict(app=app, db=db, User=User, Role=Role ,Post=Post, Follow=Follow)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    print(sys.argv)
    manager.run()
    #app.run()