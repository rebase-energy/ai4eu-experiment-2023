import logging
from concurrent import futures
import threading
import pandas as pd
import grpc
import validation.model_pb2 as model_pb2
import validation.model_pb2_grpc as model_pb2_grpc
import validation.config as config
from google.protobuf.json_format import MessageToDict 
from validation.core.validate import validate
from validation.main import run
import json

class RebaseValidationServicer(model_pb2_grpc.RebaseValidationServicer):

    def Validate(self, request, context):
        print(request.dataframe)
        print(request.rules)
        rows = json.loads(request.dataframe)
        rules = json.loads(request.rules)
        df = pd.DataFrame(rows)
        print(df)
        print(rules)
        expectations = []
        result = validate(df, expectations)

        print(result)

        key = list(result['run_results'].keys())[0]
        v = result['run_results'][key]['validation_result']
        validation_result = {
            'results': v['results'],
            'success': v['success']
        }
        print(validation_result)
 
        res = model_pb2.Result(validation_result=json.dumps(validation_result))

        return res


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    model_pb2_grpc.add_RebaseValidationServicer_to_server(
        RebaseValidationServicer(), server)
    server.add_insecure_port(f'[::]:{config.PORT}')
    server.start()
    #threading.Thread(target=run()).start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()