import logging
from concurrent import futures
import threading
import pandas as pd
import grpc
import autoregressive.model_pb2 as model_pb2
import autoregressive.model_pb2_grpc as model_pb2_grpc
import autoregressive.config as config
from autoregressive.main import run
from autoregressive.run_model import train_model, forecast
import pickle
import json

class RebaseModelService(model_pb2_grpc.RebaseModelServicer):

    def Train(self, request, context):
        train_set = request.train_set
        train_df = pd.DataFrame(json.loads(train_set))

        fit_results = train_model(train_df)

        with open('autoregressive/out/fit_results2.pkl', 'wb') as f:
            pickle.dump(fit_results, f)

        return model_pb2.Empty()

    def Predict(self, request, context):
        pred_set = request.pred_set
        pred_df = pd.DataFrame(json.loads(pred_set))

        with open('autoregressive/out/fit_results2.pkl', 'rb') as f:
            fit_results = pickle.load(f)

        
        df = forecast(fit_results, pred_df, int(request.nr_steps))
        print(df)
        return model_pb2.Result(
            result=df.to_json()
        )




def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    model_pb2_grpc.add_RebaseModelServicer_to_server(
        RebaseModelService(), server)
    server.add_insecure_port(f'[::]:{config.PORT}')
    server.start()
    #threading.Thread(target=run()).start()
    server.wait_for_termination()


if __name__ == '__main__':
    print("Starting prediction server")
    logging.basicConfig()
    serve()