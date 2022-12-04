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

        f = request.files['file']
        f.save(savePath)
        video = cv2.VideoCapture()
        fps, f_count = video.get(cv2.CAP_PROP_FPS), video.get(cv2.CAP_PROP_FRAME_COUNT)
        videoDao.insert([clientDB.Video(fps = fps,totalFrame=f_count,videoName=request.files['file'].filename, videoDirectory=savePath, clientId=clientId)])
        video.release()
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
        video.set(cv2.CAP_PROP_POS_FRAMES,start)
        for i in range(end-start+1):
            ret, frame = video.read()
            if not ret:
                print("error occure")
                break
            yield frame
        video.release()

