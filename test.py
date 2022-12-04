from SORT.sort import Sort
from projectCApp.analysisService.analysisModule.analysis import AnalysisCore
from projectCApp.analysisService.analysisModule.manager import AnalysisManger
from resource.modelFactory import YoloFactory
import os
import glob
import tensorflow as tf
from projectCApp.DB.daos import ClientDB
import time
"""
remove_list = glob.glob("test_data/car_image/*")
for file_path in remove_list:
    if os.path.exists(file_path):
        os.remove(file_path)

save_directory = "./test_data/car_set/"
label_shape = ['Van', 'bus', 'compact', 'sedan', 'suv', 'truck']
label_color = ['beige', 'black', 'blue', 'brown', 'red', 'silver', 'white', 'yellow' ]
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

user = ClientDB("hankug")
#analysisManager = AnalysisService(user,analysisCore,conditionDict,conditionLables)
analysisManager = AnalysisManger(user,analysisCore,{},conditionLables)
analysisManager.updateAnalysis("./test_data/carVideo.mp4",1,[])
"""

"""
start = time.time()
db = ClientDB("hankug")
manager = AnalysisManger(clientDB=db)
manager.selectAnalysisData2(1)
#print(manager.selectAnalysisData2(1))
print(time.time()-start)
"""