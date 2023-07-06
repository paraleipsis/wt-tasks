import uvicorn
from fastapi import FastAPI
from urllib.parse import quote

app = FastAPI()


@app.get("/encode_url/")
def encode_url(url: str):
    encoded_url = quote(url, safe='')
    return {"encoded_url": encoded_url}


if __name__ == "__main__":

    uvicorn.run(
        "encode_app:app",
        host='0.0.0.0',
        port=8001,
        reload=True
    )
