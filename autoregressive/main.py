import uvicorn
from fastapi import FastAPI, Request, Form, Response, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pickle
import simplejson
import pandas as pd
import io
from prediction import to_multiindex, get_prediction, get_params, store_result

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")





@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



@app.get("/result")
async def results(request: Request):
    try:
        with open('out/result.pickle', 'rb') as f:
            data = pickle.load(f)
            df = data['result']
            df = df['target'].to_frame()
            df = df.reset_index()
            df['ref_datetime'] = df['ref_datetime'].dt.strftime('%Y-%m-%d %H:%M')
            df['valid_datetime'] = df['valid_datetime'].dt.strftime('%Y-%m-%d %H:%M')

            result = {
                'timestamp': data['timestamp'],
                'prediction': df.to_dict(orient='list')
            }
            return Response(content=simplejson.dumps(result, ignore_nan=True))
    except Exception as e:
        print(e)
    
    return Response(status_code=404)




@app.post("/predict")
async def predict(request: Request, train_file: UploadFile, pred_file: UploadFile):
    train_df = pd.read_csv(train_file.file)
    pred_df = pd.read_csv(pred_file.file)

    params = get_params()

    # Convert to multiindex dataframe and run prediction
    df = get_prediction(
        to_multiindex(train_df),
        to_multiindex(pred_df),
        params
    )


    # Store result as cache file, UI can poll results with /result endpoint
    store_result(df)


    return 'Ok'



@app.get("/download/{name}")
async def download(request: Request, name: str):
    try:
        with open('out/result.pickle', 'rb') as f:
            data = pickle.load(f)
            df = data['result']
            stream = io.StringIO()
            
            df.to_csv(stream)
            
            response = StreamingResponse(iter([stream.getvalue()]),
                                    media_type="text/csv"
            )
            
            response.headers["Content-Disposition"] = "attachment; filename=prediction.csv"

            return response      
    except Exception as e:
        print(e)
    
    return Response(status_code=404)



def run():
    uvicorn.run('main:app', host="0.0.0.0", port=8062)
