
This project has received funding from the European Union's Horizon 2020 research and innovation programme within the framework of the I-NERGY Project, funded under grant agreement No 101016508

## Blend model

This mode combines the two algorithms: Time Regime Switching and a Blending algorithm.

The time regime switching algorithm splits the forecasts into groups based on the hour of the day and calculates separate blending weights for each group. The reasoning behind this algorithm is that some forecasts perform better during a specific period of the day (e.g. night hours) and some others during another period of the day (e.g. day hours).

The blending algorithm can be used to calculate the weighted average of multiple time-series. This can help in cases where multiple forecasts are available for a specific target (e.g. from various models, vendors, etc.). The combination of multiple forecasts usually reduces the forecast error.


# Deploy

## Kubernetes
You can deploy this in Kubernetes

1. Go to the asset [here](https://aiexp.ai4europe.eu/#/marketSolutions?solutionId=66612c50-ad86-4c96-8913-74d5d050f162&revisionId=03a1e104-6e93-409a-8da9-9f9f58dc29f5&parentUrl=mymodel#md-model-detail-template)

2. Click on "Deploy for Execution" in the top right corner, or "Sign In To Download" first if you're not logged in

3. Click on Local Kubernetes

4. unzip solution.zip

5. Create a new namespace: ``kubectl create ns <namespace>``

6. Install the deployment and service: ``python solution/kubernetes-client-script.py -n <namespace>``

7. Confirm the setup by running: ``kubectl get pods -n <namespace>``


## Install locally
From root folder run:
``pip install -r blend/requirements.txt``

## Start server
From root folder run:
``python -m blend.server``

This will start the gRPC server at http://localhost:8061 and UI at http://localhost:8062



## Test with client


Run:

``python -m blend.client``

The Blend rpc method as described in model.proto, accepts this as input:

```
Input {
    TimeseriesInput timeseries = 1;
    int32 nr_regimes = 2;
}
```

Where nr_regimes is an integer that determines how many splits that will be made. 

And timeseries has the following format:

```
TimeseriesInput {
    repeated string timestamp = 1;
    repeated float provider_a = 2;
    repeated float provider_b = 3;
    repeated float target = 4;
}
```

It accepts a forecasts from two providers A and B, as well as a target and timestamps.

For example:

```
timestamp = ['2023-11-15 00:00', '2023-11-15 01:00', ...]
provider_a = [1923.2, 1841.9, ...]
provider_b = [1739.6, 1723.3, ...]
target = [1872.13, 1852.0, ...]
```

It then returns the weighted mean of that timeseries and the meta information with the weights:

```
Result {
    WeightedMean weighted_mean = 1;
    repeated WeightRow weights = 2;

}
```

Eeach Weight Row returns a list range of hours to the weight should be applied to:

For example:
```
{hours: [0, 8], providerWeight: {a: 0.3, b: 0.7}, meta: {n_train: 5, mae_train: 2341.4}},
{hours: [8, 16], providerWeight: {a: 0.24, b: 0.74}, meta: {n_train: 5, mae_train: 20123.3}},
{hours: [17, 24], providerWeight: {a: 0.54, b: 0.46}, meta: {n_train: 5, mae_train: 17432.1}},
```



## Development

If you use this code and change anything in the protocol **model.proto**, you need to generate the new stubs:

```
./blend/restub.sh
```


