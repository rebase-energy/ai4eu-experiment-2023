

import uvicorn
from fastapi import FastAPI, Request, Form, Response, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse 
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pickle
import json
import pandas as pd
from datetime import datetime
from validation.core.validate import validate

app = FastAPI()

app.mount("/static", StaticFiles(directory="validation/static"), name="static")
app.mount("/out", StaticFiles(directory="validation/out"), name="out")


templates = Jinja2Templates(directory="validation/templates")





@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})




@app.post("/check_columns")
async def check_columns(request: Request, file: UploadFile):
    df = pd.read_csv(file.file)
    print(df)

    df.to_csv('validation/out/data.csv', index=False)

    return df.columns.tolist()




@app.post("/validate")
async def run_validate(request: Request, expectations = Form()):

    df = pd.read_csv('validation/out/data.csv')
    expectations = json.loads(expectations)
    result = validate(df, expectations)
    
    file_name = f"out/{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
    path = f"validation/{file_name}"
    with open(path, 'w+') as f:
        d = {
            'data': df.to_dict(orient='records'),
            'validation': json.loads(str(result))
        }
        f.write(json.dumps(d))

    return file_name


# @app.get("{file_name}")
# async def get_result(file_name):
#     print(file_name)
#     with open(file_name) as f:
#         return json.load(f)
    









def run():
    uvicorn.run('validation.main:app', host="0.0.0.0", port=8062)
