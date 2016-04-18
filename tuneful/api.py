import os.path
import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from tuneful import app
from .database import session
from .utils import upload_path

song_schema = {
    "properties": {
        "file": {
            "properties": {
                "id": { "type": "integer" }
            }
        }
    },
    "required": ["file"]
}

@app.route("/api/songs", methods=["GET"])
@decorators.accept("application/json")
def songs_get():
    """ Get a list of songs """
    # get the songs from the database
    songs = session.query(models.Song).all()

    # convert the songs to JSON and return a Response
    data = json.dumps([song.as_dictionary() for song in songs])
    return Response(data, 200, mimetype="application/json")
    
@app.route("/api/songs/<int:id>", methods=["GET"])
@decorators.accept("application/json")
def song_get(id):
    """ Get a song """
    # get the song from the database
    song = session.query(models.Song).get(id)

    # Check whether the song exists
    # If not return a 404 with a helpful message
    if not song:
        message = "Could not find song with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    # Return the post as JSON
    data = json.dumps(song.as_dictionary())
    return Response(data, 200, mimetype="application/json")
    
@app.route("/api/songs", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def songs_post():
    """ Add a new song """
    data = request.json

    # Check that the JSON supplied is valid
    # If not you return a 422 Unprocessable Entity
    try:
        validate(data, song_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")

    # Add the post to the database
    song = models.Song(file_id=data["file"]["id"])
    session.add(song)
    session.commit()

    # Return a 201 Created, containing the post as JSON and with the
    # Location header set to the location of the post
    data = json.dumps(song.as_dictionary())
    headers = {"Location": url_for("song_get", id=song.id)}
    return Response(data, 201, headers=headers,
                    mimetype="application/json")
