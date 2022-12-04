import os
import re
import cv2
from flask import Flask, request, Response, render_template
from flask_restx import Api, Resource
from projectCApp.DB.daos import ClientDB
from projectCApp.analysisService.analysisModule.manager import AnalysisManger
from projectCApp.analysisService.tubeDataManager.manager import TubeDataManager
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "./userVideos"
app.config['MAX_CONTENT_PATH'] = 1024*1024*1024
api = Api(app)

@api.route('/analysis-data/<string:clientId>/<int:videoId>/')
class DataManager(Resource):
    def get(self,clientId,videoId):
        client = ClientDB(clientId)
        analysisManager = AnalysisManger(clientDB=client)
        result = analysisManager.selectAnalysisData(videoId)
        return result

@api.route('/upload_file')
class UploadFile(Resource):
    def post(self):
        client = ClientDB("hankug")
        manager = TubeDataManager()
        return manager.fileSaver(client)

    def get(self):
        client = ClientDB("hankug")
        manager = TubeDataManager()
        return manager.fileSender(4,client)

@app.route('/show')
def index():
    db = ClientDB("hankug")
    manager = AnalysisManger(clientDB=db)
    data = manager.selectAnalysisData2(1)
    return render_template('4page2.html',data=data)

@app.route("/video_show")
def video():
    return Response(TubeDataManager.streamVideo("D:/pythonProjectC/test_data/carVideo.mp4"),mimetype="video/mp4")


@app.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response


def readVideoRange(path,start,end):
    video = cv2.VideoCapture(path)
    video.set(2,start)
    for i in range(end-start+1):
        ret, frame = video.read()
        if not ret:
            print("error occure")
            break
        yield frame
    video.release()

def test(path,byte1,byte2):
    result = []
    for frame in readVideoRange(path, 50, 100):
        ret, buffer = cv2.imencode('.mp4', frame)
        result.append(buffer.tobytes())

    result = b"".join(result)
    file_size = len(result)

    start = 0
    if byte1 < file_size:
        start = byte1
    if byte2:
        length = byte2 + 1 - byte1
    else:
        length = file_size - start


    return result[start:length],start,length, file_size


def dumpBBOX(path,start,end,bbox):
    count = 0
    result = []
    for frame in readVideoRange(path,start,end):
        loc = bbox[start+count]
        count+=1
        bboxImg = cv2.rectangle(frame,(loc["x1"],loc["y1"]),(loc["x2"],loc["y2"]),(0,255,0),3)
        ret, buffer = cv2.imencode('.mp4', bboxImg)
        result.append(buffer.tobytes())
    return b"".join(result)

def bboxVideo(videoId,objectId,clientDB):
    path = TubeDataManager().getVideoPath(videoId,clientDB)
    manager = AnalysisManger(clientDB=clientDB)
    video = manager.selectAnalysisData(videoId)
    obj = video["datas"][objectId]
    result = dumpBBOX(path,obj["startFrame"],obj["endFrame"],video["datas"][objectId]["frameData"])



def get_chunk(filePath,byte1=None, byte2=None):
    full_path = filePath
    file_size = os.stat(full_path).st_size
    start = 0

    if byte1 < file_size:
        start = byte1
    if byte2:
        length = byte2 + 1 - byte1
    else:
        length = file_size - start

    with open(full_path, 'rb') as f:
        f.seek(start)
        chunk = f.read(length)
    return chunk, start, length, file_size


@app.route('/video')
def get_file():
    range_header = request.headers.get('Range', None)
    byte1, byte2 = 0, None
    if range_header:
        match = re.search(r'(\d+)-(\d*)', range_header)
        groups = match.groups()

        if groups[0]:
            byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])

    chunk, start, length, file_size = get_chunk("D:/pythonProjectC/test_data/carVideo.mp4",byte1, byte2)
    resp = Response(chunk, 206, mimetype='video/mp4',
                    content_type='video/mp4', direct_passthrough=True)
    resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    return resp

@app.route('/video2')
def get_file2():
    range_header = request.headers.get('Range', None)
    byte1, byte2 = 0, None
    if range_header:
        match = re.search(r'(\d+)-(\d*)', range_header)
        groups = match.groups()

        if groups[0]:
            byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])

    chunk, start, length, file_size = test("D:/pythonProjectC/test_data/longvideo.mp4",byte1, byte2)
    resp = Response(chunk, 206, mimetype='video/mp4',
                    content_type='video/mp4', direct_passthrough=True)
    resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    return resp

if __name__ == "__main__":
    app.run(debug=True, host='localhost', port=8085)
#<img src="{{ url_for('video') }}">




