import pickle
import os
import cv2
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("ServiceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendancerealtime-2eafc-default-rtdb.firebaseio.com/",
    'storageBucket':"faceattendancerealtime-2eafc.appspot.com"
})



cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

imgBackground = cv2.imread('Resources/background.png')

# importing the mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))

# load the encoding file
print("Loading Encode File")
file = open("EncodeFile.p",'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
print("Encode File Loaded")
# print(studentIds)

modeType = 0
counter = 0
id = 0
bucket = storage.bucket()
imgStudent = []

# print(len(imgModeList))
while True:
    success, img = cap.read()

    imgS = cv2.resize(img,(0,0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    faceCurrFrame = face_recognition.face_locations(imgS)
    encodeCurrFrame = face_recognition.face_encodings(imgS,faceCurrFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    if faceCurrFrame:

        for encodeFace, faceLoc in zip(encodeCurrFrame, faceCurrFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches",matches)
            # print("faceDis" , faceDis)

            matchIndex = np.argmin(faceDis)
            # print("match index", matchIndex)

            if matches[matchIndex]:
                # print("Known Face Detected")
                # print(studentIds[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]
                #print(id)
                if counter == 0:
                    cvzone.putTextRect(imgBackground,"Loading",(275,400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1



        if counter != 0:

            if counter == 1:
                # get the data
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)
                # get the image from the storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)

                # update the data of Attendance
                datetimeObject = datetime.strptime(studentInfo['Last_Attendance_Time'],
                                                  "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed >43200:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['Total_Attendance'] +=1
                    ref.child('Total_Attendance').set(studentInfo['Total_Attendance'])
                    ref.child('Last_Attendance_Time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]


            if modeType !=3:

                if 10<counter<20:
                    modeType = 2

                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter<=10:

                    cv2.putText(imgBackground,str(studentInfo['Total_Attendance']),(861,125),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1 )
                    cv2.putText(imgBackground,str(studentInfo['Major']),(1006,550),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1 )
                    cv2.putText(imgBackground,str(id),(1006,493),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1 )
                    cv2.putText(imgBackground,str(studentInfo['Standing']),(910,625),cv2.FONT_HERSHEY_COMPLEX,1,(100,100,100),1 )
                    cv2.putText(imgBackground,str(studentInfo['Year']),(1025,625),cv2.FONT_HERSHEY_COMPLEX,1,(100,100,100),1 )
                    cv2.putText(imgBackground,str(studentInfo['Starting_Year']),(1125,625),cv2.FONT_HERSHEY_COMPLEX,1,(100,100,100),1 )

                    (w, h), _ = cv2.getTextSize(studentInfo['Name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                    offset = (414-w)//2
                    cv2.putText(imgBackground,str(studentInfo['Name']),(808+offset,445),cv2.FONT_HERSHEY_COMPLEX,1,(50,50,50),1 )

                    imgBackground[175:175+216, 909:909+216] = imgStudent

                counter+=1

                if counter>=20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent  = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0



    # cv2.imshow("face Attendance", img)
    cv2.imshow('Face Attendance', imgBackground)
    cv2.waitKey(1)




