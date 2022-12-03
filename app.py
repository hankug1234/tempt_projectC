import os
import re
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
    return render_template('4page2.html')
@app.route("/video_show")
def video():
    return Response(TubeDataManager.streamVideo("D:/pythonProjectC/test_data/carVideo.mp4"),mimetype="video/mp4")


@app.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response


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

    chunk, start, length, file_size = get_chunk("D:/pythonProjectC/test_data/longvideo.mp4",byte1, byte2)
    resp = Response(chunk, 206, mimetype='video/mp4',
                    content_type='video/mp4', direct_passthrough=True)
    resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    return resp

if __name__ == "__main__":
    app.run(debug=True, host='localhost', port=8085)
#<img src="{{ url_for('video') }}">




