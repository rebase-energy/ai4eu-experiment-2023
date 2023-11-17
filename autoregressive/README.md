
This project has received funding from the European Union's Horizon 2020 research and innovation programme within the framework of the I-NERGY Project, funded under grant agreement No 101016508

## Very-short term autoregressive model

This is an adaption of the [R code](http://www.jethrobrowell.com/uploads/4/5/4/0/45405281/vsparse_02102015.zip) that implements the Sparse Vector Autoregression (sVAR) method for very-short-term (minutes ahead) wind/solar generation forecasting. More details about the methodology can be read below.

Dowell, Jethro, and Pierre Pinson. 'Very-Short-Term Probabilistic Wind Power Forecasts by Sparse Vector Autoregression'. IEEE Transactions on Smart Grid 7, no. 2 (March 2016): 763--70. https://doi.org/10.1109/TSG.2015.2424078. and https://pure.strath.ac.uk/ws/portalfiles/portal/41930130/Dowell_Pinsen_IEEE_TSG_2015_Very_short_term_probablistic_wind_power.pdf

And test data can be found here:
https://pureportal.strath.ac.uk/files/42886878/AEMO1213.csv
http://www.jethrobrowell.com/data-and-code.html

License: BSD licence

# Deploy

## Kubernetes
You can deploy this in Kubernetes

1. Go to the asset [here](https://aiexp.ai4europe.eu/#/marketSolutions?solutionId=9323e53f-cec4-432f-b7f5-36d4c2d18c3e&revisionId=ef739b9e-1f89-4af8-a7c6-48b8dc698a5f&parentUrl=mymodel#md-model-detail-template)

2. Click on "Deploy for Execution" in the top right corner, or "Sign In To Download" first if you're not logged in

3. Click on Local Kubernetes

4. unzip solution.zip

5. Create a new namespace: ``kubectl create ns <namespace>``

6. Install the deployment and service: ``python solution/kubernetes-client-script.py -n <namespace>``

7. Confirm the setup by running: ``kubectl get pods -n <namespace>``


## Install locally

``pip install -r autoregressive/requirements.txt``

You will also need R installed. 

## Start server
From root folder of this repo run:
``python -m autoregressive.server``

This will start the gRPC server at http://localhost:8061 and UI at http://localhost:8062



## Test with client


Run:

``python -m client``

The Train rpc method as described in model.proto, requires you to pass a JSON array with the following format, where each column represents a site .


```json
[
    {"wind_farm_1": 1221.23, "wind_farm_2": 1662.75, ...,  "wind_farm_n": 2321.1},
    {"wind_farm_1": 1373.21, "wind_farm_2": 1743.12, ..., "wind_farm_n": 1889.9},
    ...
]
```

The Predict rpc method, also requires you to pass a JSON array with same format. This is the data to predict N steps ahead from. You also specify nr_steps as an integer. However, this only only meant for very-short term forecast of the next steps. 

## Development

If you use this code and change anything in the protocol **model.proto**, you need to generate the new stubs:

```
./autoregressive/restub.sh
```


