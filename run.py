from mafiapm.main import app
from mafiapm.util import sanic_config_manager


sanic_config_manager(app, prefix="SANIC_")


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port="8000",
        debug=True,
    )
