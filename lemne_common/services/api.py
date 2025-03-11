from datetime import datetime
import json


class JSON():
    def __init__(self, worker_id, worker_type):
        super().__init__()

        self.worker_id = worker_id
        self.worker_type = worker_type

    @classmethod
    def build_response(cls, id, req, type):
        response = {
            'ResponseMessage': {
                'Header': {
                    'MessageId': id,
                    'ClientApplication': 'VMS',
                    'Version': '1.0.0',
                    'Operation': type,
                    'CorrelationId': req['Header']['CorrelationId']
                },
                'BucketPath': req['BucketPath'],
                'FolderPath': req['FolderPath'],
                'FileName': req['FileName'],
            }
        }
        return response

    def decode(self, data):
        res = json.loads(data)
        return res

    def encode(self, res):
        res = json.dumps(res, indent=4)
        return res

    def response(self, id, req, result, type, *args, **kwargs):
        res = self.build_response(id, req, result, type, *args, **kwargs)
        res = self.encode(res)
        return res

