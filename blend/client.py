import pandas as pd
import grpc
import blend.model_pb2 as model_pb2
import blend.model_pb2_grpc as model_pb2_grpc
import blend.config as config
from google.protobuf.json_format import MessageToJson 
import json
from random import uniform


def blend():
    with grpc.insecure_channel(f'localhost:{config.PORT}') as channel:
        stub = model_pb2_grpc.RebaseModelStub(channel)

        timestamps = pd.date_range('2023-01-01 00:00', '2023-02-01', freq='1H')
        timestamps = [t.strftime('%Y-%m-%d %H:%M') for t in timestamps]

        ts = model_pb2.TimeseriesInput(
                timestamp=timestamps,
                provider_a=[uniform(0, 1) for _ in timestamps],
                provider_b=[uniform(0, 1) for _ in timestamps],
                target=[uniform(0, 1) for _ in timestamps],
        )

        response = stub.Blend(
            model_pb2.Input(
                timeseries=ts,
                nr_regimes=5
        ))

        return response



if __name__ == '__main__':
    response = blend()

    #print(response)
    result = json.loads(MessageToJson(response))

    print(result)
    # train_set = json.loads(result['trainSet'])
    # valid_set = json.loads(result['validSet'])

    # df = pd.DataFrame.from_dict(train_set)
    # print(df)

    # df = pd.DataFrame.from_dict(valid_set)
    # print(df)