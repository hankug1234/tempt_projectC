from flask import request, send_from_directory
from werkzeug.utils import secure_filename
import os
import time
import hashlib
import cv2

class TubeDataManager:

    def __init__(self):
        self.ALLOWED_EXTENSIONS = []
    def allowed_file(self,filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in self.ALLOWED_EXTENSIONS

    def deleteFile(self,videoId,clientDB):
        videoDao = clientDB.getVideoDao()
        video = videoDao.select(videoId)[0]
        BASE_DIR = os.path.dirname(video)
        if os.path.isfile(video.videoDirectory):
            os.remove(video.videoDirectory)
        fileList = os.listdir(BASE_DIR)
        if len(fileList) == 0:
            os.rmdir(BASE_DIR)
        videoDao.delete(videoId)

        return True


    def fileSaver(self,clientDB):
        clientId = clientDB.getClientId()
        BASE_DIR = os.getcwd()
        BASE_DIR = os.path.join(BASE_DIR,"userVideos")
        clientVideosDirectory = os.path.join(BASE_DIR,clientId)
        if not os.path.exists(clientVideosDirectory):
            os.makedirs(clientVideosDirectory)

        try:
            sha1 = hashlib.sha1(str(time.time()).encode('utf-8')).hexdigest()
        except Exception:
            sha1 = hashlib.sha1(str(time.time())).hexdigest()

        secure_name = sha1+secure_filename(request.files['file'].filename)
        savePath = os.path.join(clientVideosDirectory,secure_name)
        videoDao = clientDB.getVideoDao()
        videoDao.insert([clientDB.Video(videoName=request.files['file'].filename,videoDirectory=savePath,clientId=clientId)])

        f = request.files['file']
        f.save(savePath)
        return 'file uploaded successfully'

    def fileSender(self,videoId,clientDB):
        videoDao = clientDB.getVideoDao()
        video = videoDao.select(videoId)[0]
        path = video.videoDirectory
        BASE_DIR = os.path.dirname(path)
        FILE_NAME = os.path.basename(path)
        return send_from_directory(BASE_DIR,FILE_NAME)

    def getVideoPath(self,videoId,clientDB):
        videoDao = clientDB.getVideoDao()
        video = videoDao.select(videoId)[0]
        return video.videoDirectory

    def readVideoRange(self,path,start,end):
        video = cv2.VideoCapture(path)
        video.set(2,start)
        for i in range(end-start+1):
            ret, frame = video.read()
            if not ret:
                print("error occure")
                break
            yield frame
        video.release()

    def dumpBBOX(self,path,start,end,bbox):
        count = 0
        for frame in self.readVideoRange(path,start,end):
            loc = bbox[start+count]
            count+=1
            bboxImg = cv2.rectangle(frame,(loc["x1"],loc["y1"]),(loc["x2"],loc["y2"]),(0,255,0),3)

    @staticmethod
    def streamVideo(path):
        video = cv2.VideoCapture(path)
        while True:
            ret, frame = video.read()
            if not ret:
                break
            else:
                ret, buffer = cv2.imencode('.mp4', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n' b'Content-Type: video/mp4\r\n\r\n' + frame + b'\r\n')

    @staticmethod
    def get_chunk(filename, byte1=None, byte2=None):
        filesize = os.path.getsize(filename)
        yielded = 0
        yield_size = 1024 * 1024

        if byte1 is not None:
            if not byte2:
                byte2 = filesize
            yielded = byte1
            filesize = byte2

        with open(filename, 'rb') as f:
            content = f.read()

        while True:
            remaining = filesize - yielded
            if yielded == filesize:
                break
            if remaining >= yield_size:
                yield content[yielded:yielded + yield_size]
                yielded += yield_size
            else:
                yield content[yielded:yielded + remaining]
                yielded += remaining

#return Response(gen(Camera()),mimetype='multipart/x-mixed-replace; boundary=frame')