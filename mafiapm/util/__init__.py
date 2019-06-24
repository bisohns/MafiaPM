from os import environ

from gino.ext.sanic import Gino

from sanic import Sanic

from .helpers import Yamlizer, get_installation_access_token, get_jwt

def sanic_config_manager(app: Sanic, prefix: str = "SANIC_"):
    for variable, value in environ.items():
        if variable.startswith(prefix):
            _, key = variable.split(prefix, 1)
            app.config[key] = value


def setup_database_creation_listener(app: Sanic, database: Gino):
    database.init_app(app)
    @app.listener("after_server_start")
    async def setup_database(app: Sanic, loop):
        await database.gino.create_all()
