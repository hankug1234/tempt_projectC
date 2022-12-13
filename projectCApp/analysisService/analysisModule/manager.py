
class AnalysisManger():
    def __init__(self,clientDB=None,analysisCore=None,conditionDict=None,conditionLabels=None):
        self.analysisCore = analysisCore
        self.clientDB = clientDB
        self.conditionDict = conditionDict
        self.conditionLabels = conditionLabels
        self.matchedIdDict = {}
        self.objectDao = self.clientDB.getObjectDao()
        self.objectFrameDataDao = self.clientDB.getObjectFrameDataDao()
        self.videoPath = None
    def filter(self,target,condition):
        for key in condition.keys():
            if condition[key] == -1:
                return True
            if target[key] != condition[key]:
                return False
        return True

    def executeAnalysis(self,videoPath,conditions):
        self.videoPath = videoPath
        self.analysisCore.reset()
        executableCondition = {}
        conditionSet = set()
        for condition in conditions:
            for key in condition.keys():
                conditionSet.add(key)

        for key in list(conditionSet):
            executableCondition[key] = self.conditionDict[key]
        self.analysisCore.excuteAnalysis(videoPath=videoPath,condition=executableCondition)
        results = self.analysisCore.getAnalysisResults()

        if len(results) == 0:
            objects = self.analysisCore.getObjectsProb()
            for key in objects.keys():
                self.matchedIdDict[key] = {}

        for key in results.keys():
            count = 0
            for condition in conditions:
                if self.filter(results[key],condition):
                    count +=1
            if count == 2:
                self.matchedIdDict[key] = results[key]

    def saveAnalysisData(self,videoId):
        objects = self.analysisCore.getObjects()
        objectsProb = self.analysisCore.getObjectsProb()
        objectList = []
        objectFrameDatas = []
        for key in self.matchedIdDict.keys():
            data = {}
            data["id"] = key
            try:
                data["className"] = self.conditionLabels["shape"][self.matchedIdDict[key]["shape"]]
            except KeyError:
                data["className"] = None
            try:
                data["classColor"] = self.conditionLabels["color"][self.matchedIdDict[key]["color"]]
            except KeyError:
                data["classColor"] = None
            data["startFrame"] = objects[key][0][-1]
            data["endFrame"] = objects[key][-1][-1]
            data["videoId"] = videoId
            data["prob"] = objectsProb[key]
            obj = self.clientDB.Object(id=data["id"],className=data["className"]
                                       ,classColor=data["classColor"],startFrame=data["startFrame"]
                                       ,endFrame=data["endFrame"],videoId=data["videoId"],prob=data["prob"])
            objectList.append(obj)

        for key in self.matchedIdDict.keys():
            for loca in objects[key]:
                data = {}
                data["objectId"] = key
                data["videoId"] = videoId
                data["frameNum"] = loca[-1]
                data["x1"] = loca[0]
                data["y1"] = loca[1]
                data["x2"] = loca[2]
                data["y2"] = loca[3]
                framedata = self.clientDB.ObjectFrameData(objectId=data["objectId"],videoId=data["videoId"]
                                                          ,frameNum=data["frameNum"],x1=data["x1"]
                                                          ,y1=data["y1"],x2=data["x2"],y2=data["y2"])
                objectFrameDatas.append(framedata)
        self.objectDao.insert(objectList)
        self.objectFrameDataDao.insert(objectFrameDatas)

    def putAnalysisData(self,videoPath,videoId,condition):
        self.executeAnalysis(videoPath,condition)
        self.saveAnalysisData(videoId)

    #{videoId:,data:{objectId:,data:{className:,"classColor":,"startFrame","endFrame":,"prob":,frameData:[]}}}
    def selectAnalysisData(self,videoId):
        result = {"videoId":videoId,"datas":{}}
        objectInfo = self.objectDao.select(videoId)
        framedatas = self.objectFrameDataDao.selectVideoId(videoId)
        for obj in objectInfo:
            result["datas"][f"{obj.id}"] = {}
            result["datas"][f"{obj.id}"]["className"] = str(obj.className)
            result["datas"][f"{obj.id}"]["classColor"] = str(obj.classColor)
            result["datas"][f"{obj.id}"]["startFrame"] = str(obj.startFrame)
            result["datas"][f"{obj.id}"]["endFrame"] = str(obj.endFrame)
            result["datas"][f"{obj.id}"]["prob"] = str(obj.prob)
            result["datas"][f"{obj.id}"]["frameData"] = {}

        for frame in framedatas:
            result["datas"][f"{frame.objectId}"]["frameData"][f"{frame.frameNum}"] = {"x1":str(frame.x1),"y1":str(frame.y1),"x2":str(frame.x2),"y2":str(frame.y2)}
        return result

    def selectAnalysisData2(self,videoId):
        result = {"videoId":videoId,"datas":{}}
        objectInfo = self.objectDao.select(videoId)
        framedatas = self.objectFrameDataDao.selectVideoId(videoId)
        for obj in objectInfo:
            result["datas"][obj.id] = {}
            result["datas"][obj.id]["className"] = str(obj.className)
            result["datas"][obj.id]["classColor"] = str(obj.classColor)
            result["datas"][obj.id]["startFrame"] = obj.startFrame
            result["datas"][obj.id]["endFrame"] = obj.endFrame
            result["datas"][obj.id]["prob"] = obj.prob
            result["datas"][obj.id]["frameData"] = {}

        for frame in framedatas:
            result["datas"][frame.objectId]["frameData"][frame.frameNum] = {"x1":frame.x1,"y1":frame.y1,"x2":frame.x2,"y2":frame.y2}
        return result


    def deleteAnalysis(self,videoId):
        self.objectFrameDataDao.deleteVideoId(videoId)
        self.objectDao.delete(videoId)


    def updateAnalysis(self,videoPath,videoId,condition):
        self.deleteAnalysis(videoId)
        self.putAnalysisData(videoPath,videoId,condition)

    def deleteAllAnalysis(self):
        self.objectFrameDataDao.deleteAll()
        self.objectDao.deleteAll()


