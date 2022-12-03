import torch
import sys
class YoloFactory():
    def __init__(self,modelDirectory=None,modelName=None):
        self.modelDirectory = modelDirectory
        self.modelName = modelName
        self.model = None

    def loadModel(self):
        sys.path.insert(0, self.modelDirectory)
        self.model = torch.load(self.modelDirectory+"/"+self.modelName)
        if torch.cuda.is_available():
            device = torch.device("cuda")
            self.model.to(device)

    def setModelName(self,modelName):
        self.modelName = modelName

    def setModelDirectory(self,directory):
        self.modelDirectory = directory

    def getModel(self):
        if self.model == None:
            self.loadModel()
        return self.model
