# @Author: Rafael Direito
# @Date:   2022-10-05 18:31:57 (WEST)
# @Email:  rdireito@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-05 21:19:52

import pika, os, time
import numpy as np
import cv2
import sys
import kombu
from kombu.mixins import ConsumerMixin

# AMQP Variables
RABBIT_MQ_URL = "localhost:5672"
RABBIT_MQ_USERNAME = "myuser"
RABBIT_MQ_PASSWORD = "mypassword"


# Kombu Message Consuming Worker
class Worker(ConsumerMixin):
    def __init__(self, connection, queues):
        self.connection = connection
        self.queues = queues
        self.HOGCV = cv2.HOGDescriptor()
        self.HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        
    def detect_number_of_humans(self, frame):
        bounding_box_cordinates, weights =  self.HOGCV.detectMultiScale(frame, winStride = (4, 4), padding = (8, 8), scale = 1.03)
        return len(bounding_box_cordinates)
        person = 1
        for x,y,w,h in bounding_box_cordinates:
            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.putText(frame, f'person {person}', (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
            person += 1
        
        cv2.putText(frame, 'Status : Detecting ', (40,40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255,0,0), 2)
        cv2.putText(frame, f'Total Persons : {person-1}', (40,70), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255,0,0), 2)
        return frame

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=self.queues,
                         callbacks=[self.on_message],
                         accept=['image/jpeg'])]

    def on_message(self, body, message):
        
      
        print(message.properties)
        print(message.headers)
        msg_source = message.headers["source"]
        print(f"I received a frame from {msg_source}")
        print("I'm processing the frame...")
        
        # Process the Frame
        
        # Get the original  byte array size
        size = sys.getsizeof(body) - 33
        # Jpeg-encoded byte array into numpy array
        np_array = np.frombuffer(body, dtype=np.uint8)
        np_array = np_array.reshape((size, 1))
        # Decode jpeg-encoded numpy array 
        image = cv2.imdecode(np_array, 1)

        num_humans = self.detect_number_of_humans(image)
        print(f"The frame I received has {num_humans} humans.")

        message.ack()



exchange = kombu.Exchange("human-detection-exchange", type="direct")
queues = [kombu.Queue("human-detection-queue", exchange, routing_key="human-detection")]
with kombu.Connection(f"amqp://{RABBIT_MQ_USERNAME}:{RABBIT_MQ_PASSWORD}@{RABBIT_MQ_URL}/", heartbeat=4) as conn:
        worker = Worker(conn, queues)
        worker.run()
            