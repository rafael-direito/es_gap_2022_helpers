# @Author: Rafael Direito
# @Date:   2022-10-06 11:30:52 (WEST)
# @Email:  rdireito@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-06 11:47:04


from human_detection import Human_Detection_Module

# AMQP Variables
RABBIT_MQ_URL = "localhost:5672"
RABBIT_MQ_USERNAME = "myuser"
RABBIT_MQ_PASSWORD = "mypassword"
RABBIT_MQ_EXCHANGE_NAME = "human-detection-exchange"
RABBIT_MQ_QUEUE_NAME = "human-detection-queue"

human_detection_worker = Human_Detection_Module()

human_detection_worker.start_processing(
    broker_url=RABBIT_MQ_URL,
    broker_username=RABBIT_MQ_USERNAME,
    broker_password=RABBIT_MQ_PASSWORD,
    exchange_name=RABBIT_MQ_EXCHANGE_NAME,
    queue_name=RABBIT_MQ_QUEUE_NAME
    )
