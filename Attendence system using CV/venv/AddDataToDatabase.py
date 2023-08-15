import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("ServiceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendancerealtime-2eafc-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {

    "852741":
        {
            "Name": "Emily Blunt",
            "Major": "Economics",
            "Starting_Year": 2021,
            "Total_Attendance": 12,
            "Standing": "B",
            "Year": 1,
            "Last_Attendance_Time": "2022-12-11 00:54:34"
        },
    "963852":
        {
            "Name": "Elon Musk",
            "Major": "Physics",
            "Starting_Year": 2020,
            "Total_Attendance": 7,
            "Standing": "G",
            "Year": 2,
            "Last_Attendance_Time": "2022-12-11 00:54:34"
        },
    "564865":
        {
            "Name": "Zaheer Khan",
            "Major": "Ai & ML",
            "Starting_Year": 2021,
            "Total_Attendance": 7,
            "Standing": "G",
            "Year": 3,
            "Last_Attendance_Time": "2022-12-11 00:54:34"
        }

}

for key,value in data.items():
    ref.child(key).set(value)