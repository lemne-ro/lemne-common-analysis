import sys
import os
import io
import uuid
import numpy as np
import cv2 as cv
import imageio
from confluent_kafka import Consumer, Producer
from minio import Minio
from lemne_common.services import api, logging, util


class BaseWorker():
    def __init__(self, config):
        super().__init__()

        self.id = config.HOSTNAME
        self.type = self.__class__.__name__
        self.api = api.JSON(self.id, self.type)
        self.topic_val = config.TOPIC_VAL
        self.debug = config.DEBUG
        self.logger = logging.get_logger(f'{self.type}_{self.id}')

        self.cons = Consumer({
            'bootstrap.servers': config.KAFKA_SERVER,
            'group.id': self.type,
            'auto.offset.reset': 'earliest'
        })
        self.cons.subscribe([config.TOPIC_REQ])

        self.prod = Producer({
            'bootstrap.servers': config.KAFKA_SERVER
        })

        self.logger.info(f'{self.type} with ID: {self.id} connected to Kafka {config.KAFKA_SERVER} on {config.TOPIC_REQ}!')

        self.minio = Minio(
            config.MINIO_SERVER,
            access_key=config.MINIO_ACCESS,
            secret_key=config.MINIO_SECRET,
            secure=True
        )
        self.minio_input = config.INPUT_BUCKET
        self.minio_debug = config.DEBUG_BUCKET

        # if not self.minio.bucket_exists(self.minio_debug):
        #     self.minio.make_bucket(self.minio_debug)

        self.logger.info(f'{self.type} with ID: {self.id} connected to MINIO {config.MINIO_ACCESS} on {config.MINIO_SERVER} using buckets: {config.PRIVATE_BUCKET} {config.INPUT_BUCKET} {config.DEBUG_BUCKET}!')

        # os.makedirs('./tmp', exist_ok=True)

        self.logger.info(f'{self.type} with ID: {self.id} started!')

    def run_cycle(self):
        self.prod.poll(0)

        msg = self.cons.poll(1.0)
        if msg is None:
            return
        if msg.error():
            self.logger.error(f'Kafka read error: {msg.error()}')
            return

        data = msg.value().decode('utf-8')

        res = self.process(data)
        
        if res is not None:
            self.deliver(res)

        sys.stdout.flush()

    def run(self):
        while True:
            try:
                self.run_cycle()
            except BaseException as err:
                self.logger.error(f'RUN CYCLE EXCEPTION - {self.type}:{err}', exc_info=True);
                pass

    def deliver_callback_(self, err, msg):
        if err is not None:
            self.logger.error(f'Kafka delivery failed: {err}')
        else:
            self.logger.info(f'Kafka delivery succeeded on topic {msg.topic()} partition {msg.partition()}')

    def deliver(self, res):
        self.prod.produce(self.topic_val, res, callback=self.deliver_callback_)

    def get_image(self, path):
        try:
            response = self.minio.get_object(self.minio_input, path)
            img = cv.imdecode(np.frombuffer(response.data, dtype=np.uint8), cv.IMREAD_COLOR)
            response.close()
            response.release_conn()
        except BaseException as err:
            self.logger.error(f'Could not read image: {err}')
            return None
        return img

    # def get_video(self, path):
    #     try:
    #         vid = os.path.join('./tmp', f'{self.type}_{self.id}_{os.path.basename(path)}')
    #         self.minio.fget_object(self.minio_input, path , vid)
    #         idx = str.rindex(vid, '.')
    #         vout = vid[:idx] + '_copy' + vid[idx:]
    #         ffmpeg.input(vid).output(vout).overwrite_output().run()
    #         os.remove(vid)
    #         vid = vout

    #     except BaseException as err:
    #         self.logger.error(f'Could not read video: {err}')
    #         return None
    #     return vid

    def debug_img(self, path, name, img):
        if self.debug and img is not None:
            res, img = cv.imencode('.bmp', img)
            if not res:
                return
            img = io.BytesIO(img)
            length = img.getbuffer().nbytes
            path = f'{path}/{self.type}_{self.id}/{name}.bmp'
            self.minio.put_object(self.minio_debug, path, img, length)
            # os.makedirs(os.path.dirname(path), exist_ok=True)
            # cv.imwrite(path, img)

    def process_logger(func):
        def inner(self, req, *args, **kwargs):
            handler = logging.handle(self.logger)
            stream = handler.stream
            try:
                return func(self, req, *args, log=stream, **kwargs)
            finally:
                logging.close(self.logger, handler)
        return inner

    def process(self):
        pass

