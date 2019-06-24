import base64
import logging
import os
import time

import aiohttp
import jwt

from aiohttp import web
from gidgethub import BadRequest
from gidgethub import aiohttp as gh_aiohttp
from gidgethub import routing, sansio
from mafiapm import settings
from mafiapm.blueprint.health import health
from mafiapm.blueprint.user import user
from mafiapm.model import db
from mafiapm.util import setup_database_creation_listener
from sanic_jinja2 import SanicJinja2

from sanic import Sanic
from sanic.response import json, HTTPResponse

from .settings import APP_NAME, MPM_FILE
from .util import Yamlizer, get_installation_access_token, get_jwt


app = Sanic(__name__)
app.config.from_object(settings)
jinja = SanicJinja2(app)


app.blueprint(health)

app.blueprint(user)
setup_database_creation_listener(app, db)
router = routing.Router()


@router.register("check_suite", action="requested")
async def get_repository_contents(event, gh, *args, **kwargs):
    """
    Whenever a push is made, check for an .mpm.yml file in the repository root
    """
    repo_fullname = event.data["repository"]["full_name"]
    url = f"repos/{repo_fullname}/contents/{MPM_FILE}"
    try:
        response = await gh.getitem(url)
    except BadRequest:
        print(f"Error in retrieving {MPM_FILE} file")
        pass
    else:
        _contents = base64.b64decode(response["content"])
        # convert bytes to string
        yaml_str = "".join( chr(x) for x in _contents)
        print(yaml_str)
        # Yamlizer(yaml_str, event, gh)

@app.route("/mafia", methods=["POST"])
async def main(request):
    # print(request.load_json())
    body = request.body
    # Retrieve secret to decode message
    secret = os.environ.get("GH_SECRET")
    app_id = os.environ.get("GH_APP_ID")
    jwt = get_jwt(app_id)
    async with aiohttp.ClientSession() as session:
        gh = gh_aiohttp.GitHubAPI(session, APP_NAME)
        event = sansio.Event.from_http(request.headers, body, secret=secret)
        # Installation Id and JWT are required to generated the access token
        access_token = await get_installation_access_token(
            gh, jwt=jwt, installation_id=event.data["installation"]["id"]
        )

        gh = gh_aiohttp.GitHubAPI(
            session, APP_NAME, oauth_token=access_token["token"])
        await router.dispatch(event, gh)
    return HTTPResponse(status=200)

@app.route("/")
@jinja.template('index.html')
async def index(request):
    request['flash']('success message', 'success')
    request['flash']('info message', 'info')
    request['flash']('warning message', 'warning')
    request['flash']('error message', 'error')
    return {"greetings": "hello Sanic from world!"}