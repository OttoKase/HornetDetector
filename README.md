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

There are two options on how to download the data:

1) Manually downloading the folders from Drive and inserting them to the specified folder
2) Using the script 'download_from_drive';

#### Manually downloading

To download manually, you just have to go to the [specified folder](https://drive.google.com/drive/folders/1xACUQA76mMAXFx6LChjpo768Bej6PvYO) and download everything inside 'labels' and 'images'. The download should take a couple of minutes and after that you can insert them to 'project-hornet-detection-5/train'. This method takes all images and doesn't skip those that don't have a label.

#### Using the script

The script downloads the images slower (up to 30 minutes), but takes out images that don't have a label. The images are at first downloaded into data/images/drive/roboflow or data/images/drive/top-down folder but they can be moved to the necessary location.

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

**Moving images**

If you have downloaded the images into 'roboflow' folder then you can easily move them into 'project-hornet-detection-5' folder, which contains the training data.

```mv data/images/drive/roboflow/images/* project-hornet-detection-5/train/images/```

```mv data/images/drive/roboflow/labels/* project-hornet-detection-5/train/labels/```

## License

This project was developed as a university group project.
The code and model weights are released under the MIT License.

See the LICENSE file for details.
