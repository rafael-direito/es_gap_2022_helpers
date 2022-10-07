# Software Engineering Course Project - Human Detection Module

## Clone the repository

Start by cloning the repository: `git clone https://github.com/rafael-direito/es_gap_2022_helpers.git`

After this, move to the HumanDetection directory: `cd HumanDetection`

## Create a virtual environment and install all dependencies needed

Make sure you are running Python 3.8 or higher

``` bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Run the entities

First, start by opening 3 different terminals. Then move to the *HumanDetection* directory.

### Terminal 1
Here, you will run RabbitMQ's docker container.

To so, run the following command `docker-compose up -d`

### Terminal 2
Here, you will run the human detection module

Start by activating the virtual environment you had previously created: `source venv/bin/activate`

Then, move to the human-detection-module directory: `cd human-detection-module`

Finally, run the human-detection worker: `python3 main.py`

### Terminal 3
Here, you will run the video streaming camera

Start by activating the virtual environment you had previously created: `source venv/bin/activate`

Then, move to the camera's directory: `cd camera`

Finally, run the camera: `python3 main.py`


## Outputs

### Logs
If everything is executed properly, once you start the camera entity, you should see the following logs:

#### Camera

```text
[Camera 1] Sent a frame to the human-detection module (frame_number=546, frame_timestamp=2022-10-06 12:50:12.140264)
[Camera 1] Sent a frame to the human-detection module (frame_number=552, frame_timestamp=2022-10-06 12:50:58.140264)
[Camera 1] Sent a frame to the human-detection module (frame_number=558, frame_timestamp=2022-10-06 12:51:44.640264)
[Camera 1] Sent a frame to the human-detection module (frame_number=564, frame_timestamp=2022-10-06 12:52:31.640264)
[Camera 1] Sent a frame to the human-detection module (frame_number=570, frame_timestamp=2022-10-06 12:53:19.140264)
```


#### Human Detection Module

```text
I received the frame number 558 from camera_1, with the timestamp 2022-10-06 12:51:44.640264.
I'm processing the frame...
Frame 558 has 0 human(s), and was processed in 93.31299999999999 ms.
[!!!] INTRUDER DETECTED AT TIMESTAMP 2022-10-06 12:51:44.640264[!!!]


I received the frame number 564 from camera_1, with the timestamp 2022-10-06 12:52:31.640264.
I'm processing the frame...
Frame 564 has 0 human(s), and was processed in 98.333 ms.


I received the frame number 570 from camera_1, with the timestamp 2022-10-06 12:53:19.140264.
I'm processing the frame...
Frame 570 has 1 human(s), and was processed in 98.04599999999999 ms.


I received the frame number 576 from camera_1, with the timestamp 2022-10-06 12:54:07.140264.
I'm processing the frame...
Frame 576 has 0 human(s), and was processed in 93.348 ms.
```

### Intruder Images

The Human Detection Module will save the video frames where intruders were detected.
These frames, per default, will be saved in *human-detection-module/intruders*.

Disclaimer: Every time you run the human-detection-module's code, all previous images will be deleted.



## Troubleshooting

If you encounter any problem, please contact [Rafael Direito](mailto:rafael.neves.direito@ua.pt).

Suggestions for improving the code are welcomed. To do so, open a Pull Request.


## Tested on:
OSX Monterey 12.0.1



