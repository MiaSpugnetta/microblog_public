from app import app, cli #,db
from abstractions.database import db
from app.models import User, Post

@app.shell_context_processor
def make_shell_context():
    return{'db': db, 'User': User, 'Post': Post}


# Fully working, basic web app structured as following:

# microblog\  # here micro_copy/
#    virtualenv\  # here venv
#    app\
#       __init__.py
#       routes.py
#    microblog.py


# for the app to work need to have config.py and app.db files
