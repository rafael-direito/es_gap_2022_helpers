# @Author: Rafael Direito
# @Date:   2022-10-06 11:31:00 (WEST)
# @Email:  rdireito@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-07 11:42:57

import numpy as np
import cv2
import sys
import kombu
from kombu.mixins import ConsumerMixin
import datetime
import os
import glob


# Kombu Message Consuming Human_Detection_Worker
class Human_Detection_Worker(ConsumerMixin):

    def __init__(self, connection, queues, database, output_dir):
        self.connection = connection
        self.queues = queues
        self.database = database
        self.output_dir = output_dir
        self.HOGCV = cv2.HOGDescriptor()
        self.HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())


    def detect_number_of_humans(self, frame):
        bounding_box_cordinates, _ = self.HOGCV.detectMultiScale(
            frame,
            winStride=(4, 4),
            padding=(8, 8),
            scale=1.03
        )
        return len(bounding_box_cordinates)


    def get_consumers(self, Consumer, channel):
        return [
            Consumer(
                queues=self.queues,
                callbacks=[self.on_message],
                accept=['image/jpeg']
                )
            ]


    def on_message(self, body, message):
        # Get message headers' information
        msg_source = message.headers["source"]
        frame_timestamp = message.headers["timestamp"]
        frame_count = message.headers["frame_count"]
        frame_id = message.headers["frame_id"]

        # Debug
        print(f"I received the frame number {frame_count} from {msg_source}" +
              f", with the timestamp {frame_timestamp}.")
        print("I'm processing the frame...")

        ts_processing_start = datetime.datetime.now()
        # Process the Frame
        # Get the original  byte array size
        size = sys.getsizeof(body) - 33
        # Jpeg-encoded byte array into numpy array
        np_array = np.frombuffer(body, dtype=np.uint8)
        np_array = np_array.reshape((size, 1))
        # Decode jpeg-encoded numpy array
        image = cv2.imdecode(np_array, 1)
        num_humans = self.detect_number_of_humans(image)

        # Compute Processing Time
        ts_processing_end = datetime.datetime.now()
        processing_duration = ts_processing_end - ts_processing_start
        processing_duration_ms = processing_duration.total_seconds() * 1000

        print(f"Frame {frame_count} has {num_humans} human(s), and was " +
              f"processed in {processing_duration_ms} ms.")

        # Save to Database
        self.create_database_entry(
            camera_id=msg_source,
            frame_id=frame_id,
            num_humans=num_humans,
            ts=frame_timestamp
        )

        # Do we need to raise an alarm?
        alarm_raised = self.alarm_if_needed(
            camera_id=msg_source,
            frame_id=frame_id,
        )

        if alarm_raised:
            ts_str = frame_timestamp.replace(":", "-").replace(" ", "_")
            filename = f"intruder_camera_id_{msg_source}" \
                f"_frame_id_{frame_id}" \
                f"_frame_timestamp_{ts_str}" \
                ".jpeg"
            output_image_path = os.path.join(self.output_dir, filename)
            cv2.imwrite(output_image_path, image)
            
        print("\n")

        # Remove Message From Queue
        message.ack()


    def create_database_entry(self, camera_id, frame_id, num_humans, ts):
        num_humans_key = f"camera_{camera_id}_frame_{frame_id}_n_humans"
        timestamp_key = f"camera_{camera_id}_frame_{frame_id}_timestamp"
        self.database[num_humans_key] = num_humans
        self.database[timestamp_key] = ts


    def alarm_if_needed(self, camera_id, frame_id):
        n_human_key = f"camera_{camera_id}_frame_{frame_id}_n_humans"
        prev1_n_human_key = f"camera_{camera_id}_frame_{frame_id-1}_n_humans"
        prev2_n_human_key = f"camera_{camera_id}_frame_{frame_id-2}_n_humans"

        prev1_frame_n_humans = self.database.get(prev1_n_human_key, 0)
        curr_frame_n_humans = self.database.get(n_human_key, 0)
        prev2_frame_n_humans = self.database.get(prev2_n_human_key, 0)

        if prev1_frame_n_humans + curr_frame_n_humans + prev2_frame_n_humans >= 3:
            timestamp_key = f"camera_{camera_id}_frame_{frame_id}_timestamp"
            timestamp = self.database.get(timestamp_key, "")
            print(f"[!!!] INTRUDER DETECTED AT TIMESTAMP {timestamp}[!!!]")
            return True
        return False


class Human_Detection_Module:

    def __init__(self, output_dir):
        self.database = {}
        self.output_dir = output_dir
        self.__bootstrap_output_directory()

    def __bootstrap_output_directory(self):
        if os.path.isdir(self.output_dir):
            files = os.listdir(self.output_dir)
            for f in files:
                os.remove(os.path.join(self.output_dir, f))
        else:
            os.mkdir(self.output_dir)

    def start_processing(self, broker_url, broker_username,
                         broker_password, exchange_name, queue_name):

        # Create Connection String
        connection_string = f"amqp://{broker_username}:{broker_password}" \
            f"@{broker_url}/"

        # Kombu Exchange
        self.kombu_exchange = kombu.Exchange(
            name=exchange_name,
            type="direct",
        )

        # Kombu Queues
        self.kombu_queues = [
            kombu.Queue(
                name=queue_name,
                exchange=self.kombu_exchange
            )
        ]

        # Kombu Connection
        self.kombu_connection = kombu.Connection(
            connection_string,
            heartbeat=4
        )

        # Start Human Detection Workers
        self.human_detection_worker = Human_Detection_Worker(
            connection=self.kombu_connection,
            queues=self.kombu_queues,
            database=self.database,
            output_dir=self.output_dir
        )
        self.human_detection_worker.run()
