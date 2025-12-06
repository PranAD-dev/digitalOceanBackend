from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_default():
    return {"message":"Hello Digital Ocean"}