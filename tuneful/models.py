import os.path

from flask import url_for
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from tuneful import app
from .database import Base, engine, session

class Song(Base):
    __tablename__ = 'songs'
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    
    def as_dictionary(self):
        file_data = session.query(File).get(self.file_id)
        song_dict = {
            "id": self.id,
            "file": {
                "id": file_data.id,
                "filename": file_data.filename
            }
        }
        return song_dict

class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    song = relationship("Song", uselist=False, backref="song")

    def as_dictionary(self):
        file_dict = {
            "id": self.id,
            "filename": self.filename
        }
        return file_dict