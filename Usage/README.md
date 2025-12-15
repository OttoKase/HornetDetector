# YOLOv8-nano dockerized Jetson Inference for hornet detection 


## Requirements

- NVIDIA Jetson device
- JetPack installed (matching L4T version)
- Docker installed
- NVIDIA Container Runtime enabled

Verify:
```bash
docker info | grep -i nvidia
```

## Project Structure

```
HornetDetector
├── best_model_weights/
    └── best.pt                        # Model weights
└── Usage
    ├── Input*/                         # Input images
    ├── Output*/                        # Predictions saved here
    ├── Dockerfile
    ├── infer.py
    ├── run.sh
    └── requirements.txt

```

## Build the Docker Image:
````
docker build -f Dockerfile -t hornet-model .
````
## Running Inference

Make a folder called `Input` and move your desired images there OR specify the location of your images with `--source` when using `docker run`.
### IMPORTANT:  
The container must be started from the **parent repository** (HornetDetector):

````
docker run --rm \
  --runtime nvidia \
  -v $(pwd):/app \
  hornet-model
````



## Behavior

* Input images read from ./Input/
* Images resized to 640×640
* Predictions saved to ./output/
* Uses Jetson GPU by default
* Weights loaded from ../best_model_weights/best.pt

Right now only images are supported as input, not video feeds.



