import pandas as pd
import grpc
import validation.model_pb2 as model_pb2
import validation.model_pb2_grpc as model_pb2_grpc
import validation.config as config
from google.protobuf.json_format import MessageToJson 
import json
from random import uniform


def validate():
    with grpc.insecure_channel(f'localhost:{config.PORT}') as channel:
        stub = model_pb2_grpc.RebaseValidationStub(channel)

        rows = [
            {'col1': 100, 'col2': 150},
            {'col1': 109, 'col2': 200},
        ]
        
        expectations = [
            {
                'expectation': 'expect_column_values_to_be_between', 
                'args': [
                    'col1',
                    100,
                    148
                ]
            }
        ]

        inp = model_pb2.Input(
                dataframe=json.dumps(rows),
                rules=json.dumps(expectations)
   
        )

        response = stub.Validate(inp)

        return response



if __name__ == '__main__':
    response = validate()

    #print(response)
    result = json.loads(MessageToJson(response))

    print(result)
