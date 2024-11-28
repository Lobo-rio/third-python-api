from server.instance import server, db

from controllers.books import *
from controllers.users import *

if __name__ == "__main__":
    with server.app.app_context():
        db.create_all()
    server.run()