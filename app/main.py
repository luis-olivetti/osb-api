from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import requests
from bs4 import BeautifulSoup
import pandas as pd

from app.projetos_crawler import ProjetosCrawler
from app.proposicoes_crawler import ProposicoesCrawler

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/proposicao/gerar-excel")
def generate_excel(tipo: str, data_inicio: str, data_final: str):
    crawler = ProposicoesCrawler(tipo=tipo, data_inicio=data_inicio, data_final=data_final)
    
    try:
        links = crawler.gera_links()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    for link in links:
        resposta = requests.get(link)
        pagina = BeautifulSoup(resposta.content, 'html.parser')
        dados = crawler.obter_dados(pagina)
    
    df = pd.DataFrame(dados)
    file_path = "/tmp/proposicao.xlsx"
    df.to_excel(file_path, index=False)
    
    return FileResponse(path=file_path, filename="proposicao.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.get("/projeto/gerar-excel")
def generate_excel(especie: str, data_inicio: str, data_final: str):
    crawler = ProjetosCrawler(especie=especie, data_inicio=data_inicio, data_final=data_final)
    
    try:
        links = crawler.gera_links()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    for link in links:
        resposta = requests.get(link)
        pagina = BeautifulSoup(resposta.content, 'html.parser')
        dados = crawler.obter_dados(pagina)
    
    df = pd.DataFrame(dados)
    file_path = "/tmp/projeto.xlsx"
    df.to_excel(file_path, index=False)
    
    return FileResponse(path=file_path, filename="projeto.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")