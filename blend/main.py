

import uvicorn
from fastapi import FastAPI, Request, Form, Response, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse 
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pickle
import simplejson
import pandas as pd
import io
from blend.model.regime import get_weighted_average
from blend.model.run import calc_regime

app = FastAPI()

app.mount("/static", StaticFiles(directory="blend/static"), name="static")


templates = Jinja2Templates(directory="blend/templates")





@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})





@app.post("/calculate_weights")
async def blend(request: Request, train_file: UploadFile, nr_regimes = Form()):
    nr_regimes = int(nr_regimes)
    df = pd.read_csv(train_file.file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    df_X = df[['provider_a', 'provider_b']]
    df_y = df['target']
    weights = calc_regime(df_X, df_y, nr_regimes)

    rows = []
    for index, row in weights.iterrows():
        rows.append({
            'from': int(index[0]),
            'to': int(index[1]),
            'provider_a': float(row['weights'][0]),
            'provider_b': float(row['weights'][1])
        })

    with open('blend/out/weights.pkl', 'wb') as f:
        pickle.dump(weights, f)

    return JSONResponse(content=rows)



@app.post("/calculate_mean")
async def blend(request: Request, pred_file: UploadFile):
    df = pd.read_csv(pred_file.file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    df = df[['provider_a', 'provider_b']]
    print(df)
    try:
        with open('blend/out/weights.pkl', 'rb') as f:
            weights = pickle.load(f)
            df_w = get_weighted_average(df, weights)
            df_merged = df.join(df_w)

            print(df_merged)

            clean_df = df_merged.reset_index()
            clean_df.to_csv('blend/out/latest.csv', index=False)

            return clean_df.to_dict(orient='records')

    except Exception as e:
        print(e)



@app.get("/download")
async def download(request: Request):
    df = pd.read_csv('blend/out/latest.csv')
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
    uvicorn.run('blend.main:app', host="0.0.0.0", port=8062)
