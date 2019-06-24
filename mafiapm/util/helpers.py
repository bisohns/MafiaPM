import base64
import logging
import os
import time

import aiohttp
import jwt
import yaml
from aiohttp import web

from gidgethub import aiohttp as gh_aiohttp
from gidgethub import routing, sansio


def get_jwt(app_id):
    """ Generates a JWT for authentication by the application """
    # TODO: read is as an environment variable

    pem_file_path = os.environ.get("PEM_FILE_PATH")
    pem_file = None
    if pem_file_path:
        pem_file = open(os.environ.get("PEM_FILE_PATH"), "rt").read() or os.environ.get("PEM_KEY")
    elif os.environ.get("PEM_KEY"):
        pem_file = os.environ.get("PEM_KEY")
    else:
        raise Exception("To use JWT Authentication, specify a PEM_FILE_PATH or a PEM_KEY")
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + (10 * 60),
        "iss": app_id,
    }
    encoded = jwt.encode(payload, pem_file, algorithm="RS256")
    bearer_token = encoded.decode("utf-8")
    return bearer_token


async def get_installation_access_token(gh, jwt, installation_id):
    # doc: https: // developer.github.com/v3/apps/#create-a-new-installation-token

    access_token_url = (
        f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    )
    response = await gh.post(
        access_token_url,
        data=b"",
        jwt=jwt,
        accept="application/vnd.github.machine-man-preview+json",
    )
    # example response
    # {
    #   "token": "v1.1f699f1069f60xxx",
    #   "expires_at": "2016-07-11T22:14:10Z"
    # }

    return response


class Yamlizer(object):
    valid_types = ["builder", "project"]

    async def __init__(self, stream, event, gh):
        """ initializer to handle yaml type"""
        self.event = event
        self.gh = gh
        yaml_dict = await yaml.load(stream, Loader=yaml.Loader)
        self.dict = yaml_dict
        self.repo_fullname = self.event.data["repository"]["full_name"]
        if self.dict["type"] not in self.valid_types:
            raise AttributeError(f"type not in {self.valid_types}")
        else:
            self.type = self.dict["type"]
            await self.parse_builder()
    
    async def parse_builder(self):
        """ Parse builder for specified type """
        if self.type == "builder":
            self.project_dir = self.dict.get("project_dir", None)
            if not self.project_dir:
                raise AttributeError(f"project_dir must exist")
        if self.type == "project":
            # default title to repo name
            self.title = self.dict.get("title", self.event["name"])
            self.description = self.dict.get("description", None)
            self.source = self.dict.get("source", None)
            if self.description and self.source:
                raise AttributeError("Cannot have a source and description")
            await self.project_details()
    
    async def download(self, filename):
        url = f"repos/{self.repo_fullname}/contents/{filename}"
        try:
            response = await self.gh.getitem(url)
            _contents = base64.b64decode(response["content"])
            # convert bytes to string
            content = "".join( chr(x) for x in _contents)
            return content
        except:
            print(f"Error downloading file {filename}")
    
    def link_to_abslink(self, link):
        """ Convert a file location to raw github content """
        if not link.startswith("http://") or link.startswith("https"):
            abs_link = f"https://raw.githubusercontent.com/{self.repo_fullname}/master/{link}"
        return abs_link

    async def project_details(self):
        """ Set project details and parse """
        if not self.description:
            # parse source file to use else use default readme
            if self.source:
                source_string = await self.download(self.source)
            if not self.source:
                source_string = await self.download("readme")
            # parse description
            self.description = await self.parse_description(source_string)
            self.image = link_to_abslink(image)

    async def upload_to_builder_directory(self):
        """ Upload markdown to builder directory """
        pass
    
    async def parse_description(self, string):
        """ Parse description from a string """
        pass