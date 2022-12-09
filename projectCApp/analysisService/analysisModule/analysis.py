import numpy as np
import cv2
class AnalysisCore():
    def __init__(self,tracker=None,detector=None,labelNum=None):
        self.tracker = tracker
        self.detector = detector
        self.labelNum = labelNum
        self.objects = {}
        self.objectsProb = {}
        self.objectImage = {}
        self.frameCount = 0
        self.analysisResults={}

    def getAnalysisResults(self):
        return self.analysisResults
    def reset(self):
        del self.objects
        del self.objectImage
        del self.objectsProb
        del self.analysisResults

        self.objects = {}
        self.objectImage = {}
        self.objectsProb = {}
        self.analysisResults = {}
        self.frameCount = 0

    def setTracker(self,tracker):
        self.tracker = tracker
    def setDetector(self,detector):
        self.detector = detector
    def setlabelNum(self,labelNum):
        self.labelNum = labelNum

    def getObjects(self):
        return self.objects
    def getObjectsProb(self):
        return self.objectsProb
    def getObjectImage(self):
        return self.objectImage

    def excuteTracking(self,frame):
        self.frameCount +=1
        result = self.detector([frame]).pandas().xyxy[0]
        locations = result.to_numpy()
        locations = locations[locations[:,5] == self.labelNum][:, :-2]
        objects = self.tracker.update(locations)
        outputs = []
        for obj in objects:
            prob = obj[-1]
            try:
                obj = np.append(obj[:-1].astype(int),[self.frameCount])
                outputs.append(obj)
                self.objects[obj[-2]].append(obj)
                if self.objectsProb[obj[-2]] < prob:
                    self.objectsProb[obj[-2]] = prob
                    self.objectImage[obj[-2]] = frame[obj[1]:obj[3], obj[0]:obj[2]]

            except KeyError:
                self.objects[obj[-2]] = [obj]
                self.objectsProb[obj[-2]] = prob
                self.objectImage[obj[-2]] = frame[obj[1]:obj[3],obj[0]:obj[2]]

        return outputs

    #condition = {color:[model,dsize],shape:[model,dsize]}
    def excuteAnalysis(self,videoPath,condition,betchSize=None):
        video = cv2.VideoCapture(videoPath)
        if video.isOpened():
            fps,f_count = video.get(cv2.CAP_PROP_FPS),video.get(cv2.CAP_PROP_FRAME_COUNT)
            print("fps:" + str(fps) + "  " + "frame:" + str(f_count))

            if betchSize != None:
                f_count = betchSize

            for _ in range(int(f_count)):
                _,frame = video.read()
                self.excuteTracking(frame)

            for key in condition.keys():
                model = condition[key][0]
                for target in self.objectImage.keys():
                    s = self.objectImage[target].shape
                    if s[0] == 0 or s[1] == 0:
                        continue
                    targetImage = cv2.resize(self.objectImage[target],dsize=condition[key][1],interpolation=cv2.INTER_LINEAR)
                    predict = model.predict(np.array([targetImage]))
                    result = np.argmax(predict)
                    try:
                        self.analysisResults[target][key] = result
                    except KeyError:
                        self.analysisResults[target]={}
                        self.analysisResults[target][key] = result


