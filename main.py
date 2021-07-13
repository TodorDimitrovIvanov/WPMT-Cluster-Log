from typing import Optional

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
__log_path__ = path.dirname("/var/log/wpmt/")


class LogSave(BaseModel):
    client_id: str
    email: str
    type: str
    message: str


class LogGet(BaseModel):
    client_id: str
    type: str
    date: str
    count: Optional[int] = 0


@app.post("/log/save", status_code=200)
async def entry_save(post_data: LogSave):
    post_data_dict = post_data.dict()
    try:
        if None not in post_data_dict:
            global __log_path__
            log_path = path.join(__log_path__ + "/" + post_data_dict['type'])
            log_opened = open(log_path, 'a')
            time = datetime.datetime.utcnow()
            now = time.strftime("%b-%d-%Y/%H:%M:%S")
            entry = "[UTC][" + now + "/" + post_data_dict['type'] + "/" + post_data_dict["client_id"] + "]: " + post_data_dict["message"] + "\n"
            log_opened.write(entry)
            log_opened.close()

        return{
            "response": "Success!"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=repr(e),
            headers={"X-Error": repr(e)}
        )


@app.post("/log/get", status_code=200)
async def entry_get(post_data: LogGet):
    post_data_dict = post_data.dict()
    result = {}
    try:
        with open(__log_path__ + "/" + post_data_dict['type'], "r") as file:
            lines = file.readlines()
        print("Log File Length: ", len(lines))
        for i, line in enumerate(lines):
            # TODO: Possible conversion error here. Test and debug if necessary
            if int(post_data_dict['count']) != 0 and i <= post_data_dict['count']:
                if post_data_dict['client_id'] in line:
                    result.update({i: line})
                    # TODO: Feature: If no results are found then check in the previous days' logs
            elif int(post_data_dict['count']) == 0:
                if post_data_dict['client_id'] in line:
                    result.update({i: line})
        # The 'result' is a list of the entries that matched
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=repr(e),
            headers={"X-Error": repr(e)}
        )


if __name__ == "__main__":
    # Here we must use 127.0.0.1 as K8s doesn't seem to recognize localhost ....
    uvicorn.run(app, host='127.0.0.1', port=6902)