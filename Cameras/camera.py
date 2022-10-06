# @Author: Rafael Direito
# @Date:   2022-10-05 18:26:33 (WEST)
# @Email:  rdireito@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-05 21:21:10

import pika
import cv2
import imutils
import numpy as np
import kombu

# CAMERA VARIABLES
CAMERA_ID=1

# AMQP Variables
RABBIT_MQ_URL = "localhost:5672"
RABBIT_MQ_USERNAME = "myuser"
RABBIT_MQ_PASSWORD = "mypassword"


# Kombu Connection
conn = kombu.Connection(f"amqp://{RABBIT_MQ_USERNAME}:{RABBIT_MQ_PASSWORD}@{RABBIT_MQ_URL}/")
channel = conn.channel()
# Kombu Exchange
exchange = kombu.Exchange("human-detection-exchange", type="direct", delivery_mode=1)

# Kombu Producer
producer = kombu.Producer(exchange=exchange, channel=channel) 

# Kombu Queue
queue = kombu.Queue(name="human-detection-queue", exchange=exchange) 
queue.maybe_bind(conn)
queue.declare()



image = cv2.imread("Examples/people_1.jpg")
image = imutils.resize(image, width = min(800, image.shape[1])) 
# Encode to JPEG
result, imgencode = cv2.imencode('.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY),90])
# send a message
producer.publish(
    body=imgencode.tobytes(), 
    content_type='image/jpeg', 
    content_encoding='binary', 
    headers={"source":f"camera_{CAMERA_ID}"}
    )
print ("[x] Message sent to consumer")
