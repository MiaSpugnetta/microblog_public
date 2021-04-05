# Really not sure this is supposed to be here, but for now blueprint is useful.
# Module where the app configuration options are stored
import os

# Necessary for SQLAlchemy db. Get directory name from a specified path.
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # Configuration necessary for WTF flask form. If the configuration is not set from environment variables, provide fallback value (in this case hard-coded string).
    SECRET_KEY = os.environ.get('SECRET_KEY')  # or add hardcoded string here.

    # Configuration necessary for Flask-SQLAlchemy. If the configuration is not set from environment variables, provide fallback value. In this case it is taking the database URL from the DATABASE_URL environment variables, and if that isn't defined, it is configuring a database named app.db located in the main directory of the app, which is store in the basedir variable.

    # Provide the location of the app's database.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')  # Get the DATABASE_URL environment variable, and if that isn't defined, configures a database named app.db located in the main directory of the app, which is stored in the `basedir` variable.

    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Set to False to disable the SQLAlchemy feature that signals the app every time a change is about to be made in the db.

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = []  # ['<email address here>']
    POSTS_PER_PAGE = 5
    LANGUAGES = ['en', 'es']


