from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config


app = Flask(__name__, instance_relative_config=True)
config = Config()
app.config.from_object(config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from game_app.server import home


@app.route('/', methods=['GET', 'POST'])
def reroute_home():
    return redirect(url_for('home'))


if __name__ == "__main__":
    # connect_to_db(app)

    app.run()
    pass
