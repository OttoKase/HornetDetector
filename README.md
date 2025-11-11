## Picture download

To get images of hornets into /data/hornets, you have to run the following commands. Warning: it may take a long time to download all pictures.

To download pictures of bees, you have to change all places that call hornets in 'download_hornets.py' and then run the script.

```pip install requests```

```python scripts/download_hornets.py```

GBIF.org (06 November 2025) GBIF Occurrence Download  https://doi.org/10.15468/dl.g79yt3

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
