from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import pandas as pd

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/scrape")
def scrape_url(url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return {"title": soup.title.string if soup.title else "No title found"}

@app.get("/dataframe")
def get_dataframe():
    data = {
        "Column1": [1, 2, 3, 4],
        "Column2": ["A", "B", "C", "D"]
    }
    df = pd.DataFrame(data)
    return df.to_dict(orient="records")