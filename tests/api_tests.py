import unittest
import os
import shutil
import json
try: from urllib.parse import urlparse
except ImportError: from urlparse import urlparse # Py2 compatibility
from io import StringIO

import sys; print(list(sys.modules.keys()))
# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "tuneful.config.TestingConfig"

from tuneful import app
from tuneful import models
from tuneful.utils import upload_path
from tuneful.database import Base, engine, session

class TestAPI(unittest.TestCase):
    """ Tests for the tuneful API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create folder for test uploads
        os.mkdir(upload_path())

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

        # Delete test upload folder
        shutil.rmtree(upload_path())
        
    def test_get_empty_songs(self):
        """ Getting songs from an empty database """
        response = self.client.get("/api/songs",
            headers=[("Accept", "application/json")]
        )
    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
    
        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data, [])
        
    def test_get_songs(self):
        """ Test get songs """
        file1 = models.File(filename="file1Song")
        session.add(file1)
        session.commit()
        
        song1 = models.Song(file_id=file1.id)
        session.add(song1)
        session.commit()
        
        response = self.client.get("/api/songs",
            headers=[("Accept", "application/json")]
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        
        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(len(data), 1)
        
    def test_get_song(self):
        """ Test get song """
        file1 = models.File(filename="file1Song")
        session.add(file1)
        session.commit()
        
        song1 = models.Song(file_id=file1.id)
        session.add(song1)
        session.commit()

        response = self.client.get("/api/songs/{}".format(file1.id),
            headers=[("Accept", "application/json")]
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        song = json.loads(response.data.decode("ascii"))
        self.assertEqual(len(song), 2)
        
        self.assertEqual(song["id"], 1)
        self.assertEqual(song["file"]["filename"], "file1Song")

    def test_post_song(self):
        """ Test post song """
        file1 = models.File(filename="file1Song")
        session.add(file1)
        session.commit()
        
        data = {
            "file": {
                "id": file1.id
            }
        }

        response = self.client.post("/api/songs",
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(urlparse(response.headers.get("Location")).path,
                         "/api/songs/1")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["id"], 1)

        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 1)

        song = songs[0]
        self.assertEqual(song.id, 1)
