import pandas as pd
import grpc
import autoregressive.model_pb2 as model_pb2
import autoregressive.model_pb2_grpc as model_pb2_grpc
import autoregressive.config as config
from google.protobuf.json_format import MessageToJson 
import json





def run():
    with grpc.insecure_channel(f'localhost:{config.PORT}') as channel:
        stub = model_pb2_grpc.RebaseModelStub(channel)

        df_train = pd.read_csv('autoregressive/data/captl_wf_cathrock_train.csv')
        df_pred = pd.read_csv('autoregressive/data/captl_wf_cathrock_pred.csv')


        train_input = model_pb2.TrainInput(
            train_set=json.dumps(df_train.to_dict(orient='records'))
        )
        stub.Train(
            train_input
        )

        pred_input = model_pb2.PredInput(
            pred_set=json.dumps(df_pred.to_dict(orient='records')),
            nr_steps=3
        )
        return stub.Predict(pred_input)



if __name__ == '__main__':
    response = run()
    result = json.loads(MessageToJson(response))
