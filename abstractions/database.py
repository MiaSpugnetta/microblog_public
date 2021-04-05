# If SQLAlchemy

# Install flask-sqlalchemy in the environment. Flask_friendly wrapper for SQLAlchemy.
# Install flask-migrate. Wrapper for Alembic, db migration framework for Flask Alchemy. When structure changes the data already in the db needs to be migrated to the modified structured.
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app import app

# Create database
db = SQLAlchemy(app)  # Db is represented in he app by the db instance.

# Instance of the db migration engine
migrate = Migrate(app, db)

# Create the migration repository (`(env)$ flask db init`) in the terminal.
# Flask-Migrate adds sub command `flask db` to manage everything related to db migrations.

# Create first db migration which will include the user table that maps to the `User` db model (`(env)$ flask db migrate -m "user table"`). Automatic migration.
# The `flask db migrate` command doesn't make any changes to the db, it just generates the migration script. To apply the changes (`(env)$ flask db upgrade`).
# If not db exists, it'll be created.
