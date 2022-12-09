import os
import re
from flask import Flask, request, Response, render_template, redirect
from flask_restx import Api, Resource

from SORT.sort import Sort
from projectCApp.DB.daos import ClientDB
from projectCApp.analysisService.analysisModule.analysis import AnalysisCore
from projectCApp.analysisService.analysisModule.manager import AnalysisManger
from projectCApp.analysisService.tubeDataManager.manager import TubeDataManager
from projectCApp.analysisService.clientManager.manager import ClientManager
from resource.modelFactory import YoloFactory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "./userVideos"
app.config['MAX_CONTENT_PATH'] = 1024*1024*1024
api = Api(app)

label_shape = ['Van', 'bus', 'compact', 'sedan', 'suv', 'truck']
shapeDict = {'Van':0, 'bus':1, 'compact':2, 'sedan':3, 'suv':4, 'truck':5,'all':6}
label_color = ['beige', 'black', 'blue', 'brown', 'red', 'silver', 'white', 'yellow' ]
colorDict={'beige':0, 'black':1, 'blue':2, 'brown':3, 'red':4, 'silver':5, 'white':6, 'yellow':7,'all':-1}
label = "car"
label_num = 2

yoloFactory = YoloFactory("./resource","yolov5l.pth") # make yolov5 model factory class input: (directory path, model name)
model = yoloFactory.getModel() # get yolov5 model object
#colors = tf.keras.models.load_model('resource/EFN-model.best.h5')
#shapes = tf.keras.models.load_model("resource/cartype_model_B4_data5vs5.h5")
tracker = Sort() # tracker object use SORT

analysisCore = AnalysisCore(tracker,model,label_num) # do tracking and collect analysis data

#conditionDict = {"shape":[shapes,(300,300)],"color":[colors,(224,224)]}
conditionLables = {"shape":label_shape,"color":label_color}

@api.route("/videoList/<string:clientId>")
class ShowVideoList(Resource):
    def get(self,clientId):
        client = ClientDB(clientId)
        manager = TubeDataManager()
        result = manager.selectVideosInfo(client)
        return result


@api.route('/signUp/')
class SignUpManager(Resource):
    def get(self):
        parameters = request.args.to_dict()
        clientId = parameters["clientId"]
        clientManager = ClientManager()
        result = clientManager.checkDuplicated(clientId)
        return {"result":result}

    def post(self):
        clientId = request.form["clientId"]
        clientPw = request.form["clientPw"]
        clientManager = ClientManager()
        clientManager.makeNewClient(clientId,clientPw)
        return {"result": True}

@api.route('/signIn/')
class SignInManager(Resource):
    def post(self):
        clientId = request.form["clientId"]
        clientPw = request.form["clientPw"]
        clientManager = ClientManager()
        check = clientManager.checkDuplicated(clientId)
        if check:
            pw = clientManager.selectPassword(clientId)
            if clientPw == pw:
                return {"result":True}
        return {"result":False}




@api.route('/getObjectsInfo/<string:clientId>/<int:videoId>/')
class ObjectsManager(Resource):
    def get(self,clientId,videoId):
        client = ClientDB(clientId)
        tubeDataManager = TubeDataManager()
        analysisManager = AnalysisManger(clientDB=client)
        videoInfo = tubeDataManager.selectVideoInfo(videoId,client)
        result = analysisManager.selectAnalysisData(videoId)
        result["info"] = videoInfo
        return result

@api.route('/getVideosInfo/<string:clientId>/')
class VideosManager(Resource):
    def get(self,clientId):
        clientDB = ClientDB(clientId)
        tubeDataManager = TubeDataManager()
        result = tubeDataManager.selectVideosInfo(clientDB)
        return result


@api.route('/file/<string:clientId>')
class UploadFile(Resource):
    def post(self,clientId):
        client = ClientDB(clientId)
        manager = TubeDataManager()
        return manager.fileSaver(client)

@api.route('/file/<string:clientId>/<int:videoId>')
class DownLoadFile(Resource):

    def get(self,clientId,videoId):
        client = ClientDB(clientId)
        manager = TubeDataManager()
        return manager.fileSender(videoId,client)

@api.route('/execute/<string:clientId>/<int:videoId>')
class DoAnalysis(Resource):
    def post(self,clientId,videoId):
        cars = request.form["cars"]
        colors = request.form["colors"]
        condition = [{"shape":shapeDict[cars]},{"color":colorDict[colors]}]

        client = ClientDB(clientId)
        analysisManager = AnalysisManger(client, analysisCore, {}, conditionLables)
        tubeDataManager = TubeDataManager()
        videoInfo = tubeDataManager.selectVideoInfo(videoId, client)
        analysisManager.updateAnalysis(videoInfo["videoDirectory"], videoId, condition)

        return redirect(request.referrer+f"/file/show?videoId={videoId}")



@app.route('/show')
def index():
    db = ClientDB("hankug")
    manager = AnalysisManger(clientDB=db)
    data = manager.selectAnalysisData2(1)
    return render_template('4page2.html',data=data)

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
    parameters = request.args.to_dict()
    clientId = parameters["clientId"]
    videoId = parameters["videoId"]
    tubeDataManager = TubeDataManager()
    client = ClientDB(clientId)
    videoInfo = tubeDataManager.selectVideoInfo(videoId, client)
    path = videoInfo["videoDirectory"]
    range_header = request.headers.get('Range', None)
    byte1, byte2 = 0, None
    if range_header:
        match = re.search(r'(\d+)-(\d*)', range_header)
        groups = match.groups()

        if groups[0]:
            byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])

    chunk, start, length, file_size = get_chunk(path,byte1, byte2)
    resp = Response(chunk, 206, mimetype='video/mp4',
                    content_type='video/mp4', direct_passthrough=True)
    resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    return resp

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8085)




