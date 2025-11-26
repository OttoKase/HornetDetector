import os
from roboflow import Roboflow
from dotenv import load_dotenv

load_dotenv()

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
rf = Roboflow(api_key=ROBOFLOW_API_KEY)

project = rf.workspace("hornets-kfaxc").project("project-hornet-detection-bbpor")
version = project.version(5)
dataset = version.download("yolov8")