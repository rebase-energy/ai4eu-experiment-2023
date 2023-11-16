

import uvicorn
from fastapi import FastAPI, Request, Form, Response, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse 
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pickle
import simplejson
import pandas as pd
import io
from autoregressive.util import install
from autoregressive.run_model import train_model, forecast


app = FastAPI()

app.mount("/static", StaticFiles(directory="autoregressive/static"), name="static")


templates = Jinja2Templates(directory="autoregressive/templates")

# Install some R stuff
install()



@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})





@app.post("/train")
async def train(request: Request, train_file: UploadFile):

    train_df = pd.read_csv(train_file.file)
    print(train_df)

    fit = train_model(train_df)

    with open('autoregressive/out/fit_results.pkl', 'wb') as f:
        pickle.dump(fit, f)


@app.post("/predict")
async def predict(request: Request, pred_file: UploadFile, nr_steps = Form()):
    pred_df = pd.read_csv(pred_file.file)
    print(pred_df)

    with open('autoregressive/out/fit_results.pkl', 'rb') as f:
        fit_results = pickle.load(f)


    df = forecast(fit_results, pred_df, int(nr_steps))
    df.to_csv('autoregressive/out/latest.csv', index=False)

    return df.to_dict(orient='records')



@app.get("/download")
async def download(request: Request):
    df = pd.read_csv('autoregressive/out/latest.csv')
    print(df)
    stream = io.StringIO()  
    df.to_csv(stream, index=False)
    
    response = StreamingResponse(iter([stream.getvalue()]),
                            media_type="text/csv"
    )
    
    name = 'latest'
    response.headers["Content-Disposition"] = f"attachment; filename={name}.csv"

    return response      



def run():
    uvicorn.run('autoregressive.main:app', host="0.0.0.0", port=8062)
