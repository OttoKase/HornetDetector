# Hornet Detection

This repository contains a model that predicts whether a image has a hornet or not. The model is made to use by beehive keepers, who can have this model detect hornets infront of an beehive entrance.

## Setup

The first thing, that should be done, is to download the requirements.

```pip install -r requirements.txt```

The next step is to copy the example .env file and add any necessary API keys to it. Currently only RoboFlow API key would be necessary to download the labelled pictures.

```cp .env.example .env```

### Unlabelled picture download

To get images of bees and/or hornets, you have to run the following script. Warning: it may take a long time to download all pictures. If you stop the script at one point, and then reactivate it later, it will begin where it was last stopped.

```python scripts/data_download/download_from_roboflow.py```

To change which type of bugs you want to download, you have to change the 'BUG_TYPE' variable in the .env file. Only 'bees' and 'hornets' are valid.

The pictures were downloaded from GBIF.org (06 November 2025) GBIF Occurrence Download  https://doi.org/10.15468/dl.g79yt3.

### Manually labelled picture download

To download labelled pictures, you need to insert you Roboflow API into the .env file. This can be found in Roboflow Settings -> Workspaces -> hornets -> API Keys or using [this link](https://app.roboflow.com/hornets-kfaxc/settings/api). There should be a **Private API Key** that can be copied.

After the API Key has been inserted you can just run the script that downloads labelled pictures. The version can easily be changed in the script in the ```version = project.version(5)``` row. This should download the pictures into a folder named ***project-hornet-detection-5*** that has data in train-test-val folders in YOLOv8 format.

```python scripts/data_download/download_from_roboflow.py```

### Automatically labelled picture download

Before running the script, you must obtain a **Service Account JSON key** file named ```credentials.json``` and place it in the root of your project directory.

**How to Generate ```credentials.json```?**

1) **Create a Google Cloud Project**: Go to the Google Cloud Console, create a new project, and enable the Google Drive API for that project.
2) **Create Service Account**: Navigate to IAM & Admin > Service Accounts. Create a new service account (e.g., drive-downloader).
3) **Generate Key**: Click on the new service account, go to the KEYS tab, click ADD KEY > Create new key, and choose JSON. A file will automatically download.
4) **Rename and Place**: Rename the downloaded file to ```credentials.json``` and place it in the root of this project.

**Configuration (.env file)**

Inside your .env file, you must specify the Folder code for the dataset you wish to download and declare which one is currently active. Currently there are two options: ```roboflow``` and ```top-down```.

To get the pictures into specified folders in .env file, you need to run the following script. The script has resume functionality, which means that when stopped and rerun, it will begin where it last left off.

```python scripts/data_download/download_from_drive.py```

## Task description

Problem statement: 
Hornet attacks pose a serious threat to beekeepers and their colonies. These aggressive insects can quickly destroy entire bee colonies within hours, reducing honey production and weakening hives. Early detection is critical, but traditional monitoring methods are slow and unreliable. The goal of this project is to develop an automated detection system that can identify hornets in video footage or images captured at beehive entrances. Such a system could help alert beekeepers early enough to take preventive action. 

Objectives: 
The objective is to create and train a model capable of distinguishing hornets from bees in still images (and later extendable to video frames). We would be satisfied with >80% accuracy. The final model has to work on the edge device setup at the beehive entrance.

Data: 
Base data of hornet photos will be collected manually from online sources (https://www.inaturalist.org/observations?taxon_id=54328&view=species). That base would then need to be cleaned from irrelevant or low-quality images (e.g. photos showing combs, plants, dead hornets, or unclear objects). We are thinking of using clustering for this step to find photos that include mainly hornets themselves and less noise. After cleaning, the remaining images will be labeled as hornets and added to a more general sample of data containing both hornets and other noise including regular bees. 

Methodology:
Clustering for cleaning the data, supervised models to detect hornets (K-nearest neighbours or decision tree), using cross validation to find the best model. If the data is too high dimensional then unsupervised models with PCA to reduce dimensionality and computing time. Training a neural network is certainly an alternative approach we plan to explore, though our expectations are limited due to the constraints of the edge devices available to us. Furthermore, as the course progresses we also might learn more methods that might be best suited for this project.

Evaluation:
We can evaluate our model by multiple metrics and methods. First would be to leave a chunk of available data out of training set and use it as test data, but the better evaluation would be to test on the video data where our model would actually be put to use. Measure precision, recall, F1 score, false positives and negatives. 
In our case, we also need to test the model in the field to ensure it functions properly in its intended use case, which is on edge devices.

Expected challenges:
Data quality and labeling: collecting enough high-quality images with consistent labeling will be challenging, since the dataset must be manually collected and annotated by our team.
The model must run on an edge device like Jetson Nano or Jetson Orin.
The resulting model will be applied on video data, so the detection speed is important.


Resources and tools: 
The plan is to start by using local environments. Using sklearn, tensorflow, numpy, pandas in Python through Google Colab.
