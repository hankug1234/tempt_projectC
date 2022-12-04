import tensorflow as tf
from resource.modelFactory import YoloFactory
from SORT.sort import Sort
import cv2
from projectCApp.analysisService.analysisModule.analysis import AnalysisCore
import numpy as np
import glob

#color_list = glob.glob("D:/ai/color_recognition/src/training_dataset/*")
#color_list_0 = glob.glob(color_list[0]+"/*")
#model = tf.keras.models.load_model("resource/car_color_model.h5")
#label = ['beige','black','blue','brown','gold',	'green','grey','orange','pink','purple','red','silver','tan','white','yellow']
#label_color = ['beige', 'black', 'blue', 'brown', 'red', 'silver', 'white', 'yellow' ]
#d_b={0: 'black',1:'blue',2:'cyan',3:'gray',4:'green',5:'red',6:'white',7:'yellow'}
"""
for color in color_list_0:
    img = cv2.imread(color)
    img = cv2.resize(img,dsize=(224,224),interpolation=cv2.INTER_LINEAR)
    predict = model.predict(np.array([img]))
    print(label_color[np.argmax(predict)])
"""


"""
yoloFactory = YoloFactory("./resource","yolov5l.pth") # make yolov5 model factory class input: (directory path, model name)
detector = yoloFactory.getModel()
tracker = Sort()






analysisCore = AnalysisCore(tracker,detector,2)
video = cv2.VideoCapture('test_data/carVideo.mp4')
if video.isOpened():
    print("opend")
else:
    print("fail")

while video.isOpened():
    ret,frame = video.read()
    objects = analysisCore.excuteTracking(frame)
    key = cv2.waitKey(1)
    if key == ord("q"):
        break
    for l in objects:
        x1, y1, x2, y2 = l[0], l[1], l[2], l[3]
        img = cv2.resize(frame[y1:y2,x1:x2],dsize=(100,100),interpolation=cv2.INTER_LINEAR)
        predict = model.predict(np.array([img]))
        color = label[np.argmax(predict)]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, color + ":" + str(l[4]), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    cv2.imshow("car_video_test", frame)

video.release()
"""

def readVideoRange(path,start,end):
    video = cv2.VideoCapture(path)
    video.set(cv2.CAP_PROP_POS_FRAMES,start)
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

    return result[start:length]

print(test("D:/pythonProjectC/test_data/longvideo.mp4",50,100))