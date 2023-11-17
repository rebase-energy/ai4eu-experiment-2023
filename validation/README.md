
This project has received funding from the European Union's Horizon 2020 research and innovation programme within the framework of the I-NERGY Project, funded under grant agreement No 101016508

## Data validation

Data validation node that builds on https://greatexpectations.io. It expects a dataframe like JSON string and rules “expectations” to run on the different columns.

It currently supports the expect_columns_to_be_between method

# Deploy

## Kubernetes
You can deploy this in Kubernetes

1. Go to the asset [here](https://aiexp.ai4europe.eu/#/marketSolutions?solutionId=2013f9d1-15ad-4f42-8bf7-f91443e724d6&revisionId=d21feb45-0766-4654-be9b-008c47c02063&parentUrl=mymodel#md-model-detail-template)

2. Click on "Deploy for Execution" in the top right corner, or "Sign In To Download" first if you're not logged in

3. Click on Local Kubernetes

4. unzip solution.zip

5. Create a new namespace: ``kubectl create ns <namespace>``

6. Install the deployment and service: ``python solution/kubernetes-client-script.py -n <namespace>``

7. Confirm the setup by running: ``kubectl get pods -n <namespace>``


## Install locally
From root folder run:
``pip install -r validation/requirements.txt``

## Start server
From root folder run:
``python -m validation.server``

This will start the gRPC server at http://localhost:8061 and UI at http://localhost:8062



## Test with client


Run:

``python -m validation.client``

The Validate rpc method as described in model.proto, accepts this as input:

```
Input {
    string dataframe = 1;
    string rules = 2;
}
```

Where dataframe is for example a JSON Array with the format:

```json
[
    {"wind_farm_1": 1221.23, "wind_farm_2": 1662.75, ...,  "wind_farm_n": 2321.1},
    {"wind_farm_1": 1373.21, "wind_farm_2": 1743.12, ..., "wind_farm_n": 1889.9},
    ...
]
```

And rules:

```json
[
    {
        "expectation": "expect_column_values_to_be_between", 
        "args": [
            "wind_farm_1",
            0,
            2200
        ]
    },
    {
        "expectation": "expect_column_values_to_be_between", 
        "args": [
            "wind_farm_2",
            0,
            2200
        ]
    }
]
```

And it returns this validation result:

```
Result {
    string validation_result = 1;
}

```

where validation_result is a JSON object:
```JSON
{
    "success": true | false // depending on if validaton succeeded,
    "results": [
        {
            "success": false, 
            "expectation_config": {
                "expectation_type": "expect_column_values_to_be_between", 
                    "kwargs": {
                        "column": "wind_farm_1", 
                        "min_value": 0, 
                        "max_value": 2200, "batch_id": "default_pandas_datasource-#ephemeral_pandas_asset"
                    }, 
                    "meta": {}
                }, 
                "result": {
                    "element_count": 100, 
                    "unexpected_count": 7, 
                    "unexpected_percent": 7, 
                    "partial_unexpected_list": [
                        -5.2, -13.2, 2324.2,  2324.2,  2324.2,  2324.2,  2324.2, 
                    ], 
                    "missing_count": 0, 
                    "missing_percent": 0.0, 
                    "unexpected_percent_total": 22.916666666666664, "unexpected_percent_nonmissing": 22.916666666666664, "partial_unexpected_index_list": [0, 2, 4, 41, 42, 180, 181], "partial_unexpected_counts": [
                        {"value": -5.2, "count": 1}, 
                        {"value":  -13.2, "count": 1}, 
                        {"value": 324.2, "count": 5}, 
                        {"value": 0.35, "count": 3}
                        ]
                    }, 
                    "meta": {}, 
                    "exception_info": {
                        "raised_exception": false, 
                        "exception_traceback": null, 
                        "exception_message": null}
                }   
                ....
    ]

}
```



## Development

If you use this code and change anything in the protocol **model.proto**, you need to generate the new stubs:

```
./validation/restub.sh
```


