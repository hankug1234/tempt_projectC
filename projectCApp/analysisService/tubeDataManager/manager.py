from flask import request, send_from_directory, redirect
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
        video = cv2.VideoCapture(savePath)
        fps, f_count,width,height = video.get(cv2.CAP_PROP_FPS), video.get(cv2.CAP_PROP_FRAME_COUNT),video.get(cv2.CAP_PROP_FRAME_WIDTH),video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        videoDao.insert([clientDB.Video(width=width,height=height,fps = fps,totalFrame=f_count,videoName=request.files['file'].filename, videoDirectory=savePath, clientId=clientId)])
        video.release()
        return redirect(request.referrer)

    def fileSender(self,videoId,clientDB):
        videoDao = clientDB.getVideoDao()
        video = videoDao.select(videoId)[0]
        path = video.videoDirectory
        BASE_DIR = os.path.dirname(path)
        FILE_NAME = os.path.basename(path)
        return send_from_directory(BASE_DIR,FILE_NAME)

    def selectVideosInfo(self,clientDB):
        videoDao = clientDB.getVideoDao()
        videos = videoDao.selectAll()
        videoDict = {}
        for video in videos:
            videoDict[video.id] = {}
            videoDict[video.id]["videoName"] = video.videoName;
            videoDict[video.id]["videoDiretory"] = video.videoDirectory;
            videoDict[video.id]["fps"] = video.fps;
            videoDict[video.id]["totalFrame"] = video.totalFrame;
            videoDict[video.id]["width"] = video.width;
            videoDict[video.id]["height"] = video.height;
        return videoDict

    def selectVideoInfo(self,videoId,clientDB):
        videoDao = clientDB.getVideoDao()
        video = videoDao.select(videoId)[0]
        info = {}
        info["videoName"] = video.videoName
        info["videoDirectory"] = video.videoDirectory
        info["fps"] = video.fps
        info["totalFrame"] = video.totalFrame
        info["width"] = video.width
        info["height"] = video.height

        return info

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

