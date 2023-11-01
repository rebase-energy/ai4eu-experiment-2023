import pandas as pd
import grpc
import model_pb2 as model_pb2
import model_pb2_grpc as model_pb2_grpc
import config as config
from google.protobuf.json_format import MessageToJson 
import json



def get_data():
    with grpc.insecure_channel(f'localhost:{config.PORT}') as channel:
        stub = model_pb2_grpc.RebaseDatasetStub(channel)

        return stub.LoadData(
            model_pb2.Empty()
        )



if __name__ == '__main__':
    response = get_data()
    result = json.loads(MessageToJson(response))
    train_set = json.loads(result['trainSet'])
    valid_set = json.loads(result['validSet'])

    df = pd.DataFrame.from_dict(train_set)
    print(df)

    df = pd.DataFrame.from_dict(valid_set)
    print(df)