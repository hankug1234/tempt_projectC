from sqlalchemy import Column, Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
#from connections import Engine

def makeClientsTable(base):
    class Client(base):
        __tablename__ = "clients"
        id = Column(String(50),primary_key=True)
        pw = Column(String(50))

        video = relationship("Video",back_populates="client")

        def asDict(self):
            return self.__dict__
        def __repr__(self):
            return f"Client(id={self.id!r}, pw={self.pw!r})"
    return Client

def makeVideosTable(base,clientId_):
    class Video(base):
        __tablename__ = f"{clientId_}_videos"
        id = Column(Integer,primary_key=True,autoincrement=True)
        videoName = Column(String(100))
        videoDirectory = Column(String(300))
        clientId = Column(String(50),ForeignKey("clients.id"))

        client = relationship("Client",back_populates="video")
        object = relationship("Object",back_populates="video")

        def asDict(self):
            return self.__dict__
        def __repr__(self):
            return f"Video(id={self.id!r},videoName={self.videoName!r},videoDirectory={self.videoDirectory!r},clientId={self.clientId})"
    return Video

def makeObjectsTable(base,clientId):
    class Object(base):
        __tablename__ = f"{clientId}_objects"
        id = Column(Integer,primary_key=True,autoincrement=True)
        className = Column(String(50))
        classColor = Column(String(20))
        startFrame = Column(Integer)
        endFrame = Column(Integer)
        prob = Column(Float)
        videoId = Column(Integer,ForeignKey(f"{clientId}_videos.id"),primary_key=True)

        video = relationship("Video",back_populates="object")
        objectFrameData = relationship("ObjectFrameData",back_populates="object")

        def asDict(self):
            return self.__dict__
        def __repr__(self):
            return f"Object(id={self.id!r}, className={self.className!r}, startFrame={self.startFrame}, endFrame={self.endFrame}, videoId={self.videoId}, prob={self.prob})"

    return Object

def makeObjectFrameDatasTable(base,clientId):
    class ObjectFrameData(base):
        __tablename__ = f"{clientId}_objectFrameDatas"
        objectId = Column(Integer,ForeignKey(f"{clientId}_objects.id"),primary_key=True)
        frameNum = Column(Integer,primary_key=True)
        videoId = Column(Integer,ForeignKey(f"{clientId}_videos.id"),primary_key=True)
        x1 = Column(Integer)
        x2 = Column(Integer)
        y1 = Column(Integer)
        y2 = Column(Integer)

        object = relationship("Object",back_populates="objectFrameData")

        def asDict(self):
            return self.__dict__
        def __repr__(self):
            return f"ObjectFrameData(objectId={self.objectId!r}, frameNum={self.frameNum!r}, videoId={self.videoId},x1={self.x1},x3={self.x2},y1={self.y1},y2={self.x2})"
    return ObjectFrameData

"""
engine = Engine()

videosTable = makeVideosTable(Base,"hanmin")
objectsTable = makeObjectsTable(Base,"hanmin")
objectFrameDatasTable = makeObjectFrameDatasTable(Base,"hanmin")

Base.metadata.create_all(engine.getConnection())
"""