from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from .mysecretstuff import sentry_dsn

# Sentry stuff
sentry_sdk.init(
    dsn=sentry_dsn,
    integrations=[FlaskIntegration()]
)

#def create_app():
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstrap = Bootstrap(app)

# db init
from .models import Script
from .models import Line
from .models import Comment

db.init_app(app)
migrate = Migrate(app, db)

# blueprint for non-auth parts of app
from .main import main as main_blueprint
app.register_blueprint(main_blueprint)

###  ADMIN 
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from .admin import AdminView

app.config['FLASK_ADMIN_SWATCH'] = 'cosmo'

admin = Admin(app, name='Admin', index_view=AdminView(Script, db.session, url='/admin', endpoint='admin'))
admin.add_view(AdminView(Line, db.session))
admin.add_view(AdminView(Comment, db.session))


