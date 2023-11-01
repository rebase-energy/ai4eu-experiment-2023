import logging
from concurrent import futures
import threading
import pandas as pd
import grpc
import model_pb2
import model_pb2_grpc
import config
from google.protobuf.json_format import MessageToDict 
import simplejson
from prediction import get_prediction, evaluate, to_df, get_params, store_result
from main import run


class RebaseModelService(model_pb2_grpc.RebaseModelServicer):

    def Evaluate(self, request, context):
        train_set = request.train_set
        valid_set = request.valid_set

        df_train = to_df(train_set)
        df_test = to_df(valid_set)

        params = get_params()

        score = evaluate(df_train, df_test, params)

        print(score)

        return model_pb2.Metrics(score=simplejson.dumps(score))

    def Predict(self, request, context):

        train_set = request.train_set
        pred_set = request.pred_set

        df_train = to_df(train_set)
        df_pred = to_df(pred_set)

        params = get_params()
        print("Run predict")
        df = get_prediction(df_train, df_pred, params)

        # Store result as a cached file, then UI can poll this file
        store_result(df)

        print("Predict result")
        print(df)
        df = df.reset_index()
        df['ref_datetime'] = df['ref_datetime'].dt.strftime('%Y-%m-%d %H:%M')
        df['valid_datetime'] = df['valid_datetime'].dt.strftime('%Y-%m-%d %H:%M')


        result = model_pb2.Result(
            ref_datetime=df['ref_datetime'].tolist(),
            valid_datetime=df['valid_datetime'].tolist(),
            target=df['target'].tolist()
        )

        return result



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    model_pb2_grpc.add_RebaseModelServicer_to_server(
        RebaseModelService(), server)
    server.add_insecure_port(f'[::]:{config.PORT}')
    server.start()
    threading.Thread(target=run()).start()
    server.wait_for_termination()


if __name__ == '__main__':
    print("Starting prediction server")
    logging.basicConfig()
    serve()