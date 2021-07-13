from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import uvicorn
from os import path
import datetime

app = FastAPI()

__master_url__ = "https://master.wpmt.org"
__cluster_name__ = "cluster-eu01.wpmt.org"
__cluster_url__ = "https://cluster-eu01.wpmt.tech"
__cluster_locale__ = "EU"
__log_path__ = path("/var/log/wpmt/")


class LogSave(BaseModel):
    client_id: str
    email: str
    type: str
    err_message: str


class LogGet(BaseModel):
    client_id: str
    type: str
    date: str


@app.post("/log/save", status_code=200)
async def entry_save(post_data: LogSave):
    post_data_dict = post_data.dict()

    if None not in post_data_dict:
        global __log_path__
        log_path = path.join(__log_path__ + post_data_dict['type'])
        log_opened = open(log_path, 'a')
        time = datetime.now().strftime("%b %d %Y %H:%M:%S")
        print("Time: ", time, "Type: ", type(time))
        log_opened.write("[", time, "]:[", post_data_dict['type'], "]:[", post_data_dict["client_id"], "]:", post_data_dict["err_message"])
        log_opened.close()

    return{
        "response": "Success!"
    }


@app.post("/log/get", status_code=200)
async def entry_get(post_data: LogGet):
    post_data_dict = post_data.dict()


if __name__ == "__main__":
    # Here we must use 127.0.0.1 as K8s doesn't seem to recognize localhost ....
    uvicorn.run(app, host='127.0.0.1', port=6903)