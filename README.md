This is a web application written in Python with the Flask framework.

To make it run create a virtual environment (conda is recommended, https://repo.anaconda.com), `conda create --name <myenv>`, where `<myenv>'` is the name of the new environment. 
Activate the virtual environment, then run `pip install -r requirements.txt`.


Add a configuration file config.py (here config_dummy_file.py) containing a Config class with the following variables:
- SECRET_KEY
- SQLALCHEMY_DATABASE_URI (database configuration, in this case SQLAlchemy to run the Flask-SQLAlchemy extension, provides the location of the app's database)
- MAIL_SERVER
- MAIL_PORT
- MAIL_USE_TLS
- MAIL_USERNAME
- MAIL_PASSWORD
- ADMINS
- POSTS_PER_PAGE
- LANGUAGES    

Set up the database and initialise by running `flask db init`. Then create the first database migration by running `flask db migrate -m "users table"` and apply these changes to the database `flask db upgrade`.

To run the application `flask run`.
