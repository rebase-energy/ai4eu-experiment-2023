import logging
from concurrent import futures
import threading
import pandas as pd
import grpc
import blend.model_pb2 as model_pb2
import blend.model_pb2_grpc as model_pb2_grpc
import blend.config as config
from google.protobuf.json_format import MessageToDict 
from blend.model.run import calc_regime
from blend.main import run
from blend.model.regime import get_weighted_average


class RebaseModelService(model_pb2_grpc.RebaseModelServicer):

    def Blend(self, request, context):
        df = pd.DataFrame({
            'provider_a': list(request.timeseries.provider_a),
            'provider_b': list(request.timeseries.provider_b),
            'target': list(request.timeseries.target)
        }, index=pd.to_datetime(list(request.timeseries.timestamp)))
        df_X = df[['provider_a', 'provider_b']]

        print(df_X)

        df_y = df['target']
        print(df_y)

        nr_regimes = int(request.nr_regimes)
        print("nr_regimes:", nr_regimes)

        weights = calc_regime(df_X, df_y, nr_regimes)
        weighted_mean = get_weighted_average(df_X, weights)
    


        w_d = []

        for index, row in weights.iterrows():
            provider_weights = model_pb2.ProviderWeight(
                provider_a=row['weights'][0],
                provider_b=row['weights'][1],
            )
            meta = model_pb2.Meta(n_train=row['n_train'], mae_train=row['mae_train'])
            weight_row = model_pb2.WeightRow(
                hours=[index[0], index[1]],
                weights=provider_weights,
                meta=meta
            )
            w_d.append(weight_row)

        weighted_mean = weighted_mean.reset_index()
        weighted_mean = weighted_mean.rename(columns={'index': 'timestamp', 'Weighted Mean': 'value'})
        weighted_mean['timestamp'] = weighted_mean['timestamp'].dt.strftime('%Y-%m-%d %H:%M')


        w_mean = model_pb2.WeightedMean(
           timestamp=weighted_mean['timestamp'].values.tolist(),
           value=weighted_mean['value'].values.tolist()
        )

        result = model_pb2.Result(
            weighted_mean=w_mean,
            weights=w_d

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