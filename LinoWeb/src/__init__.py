# -*- coding: utf-8 -*-
# @Author: stephen.zlu
# @Date:   2019-09-09 09:40:13
# @Last Modified by:   stephen.zlu
# @Last Modified time: 2019-09-15 23:20:21

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import configs

db = SQLAlchemy()
migrate = Migrate()

def create_app(testing=False):
    app = Flask(__name__)

    if testing:
        app.config.from_object(configs['testing'])
    else:
        app.config.from_object(configs[app.env])

    db.init_app(app)
    migrate.init_app(app, db)

    from . import view
    app.register_blueprint(view.bp)

    return app
