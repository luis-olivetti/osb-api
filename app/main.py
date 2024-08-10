from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import requests
from bs4 import BeautifulSoup
import pandas as pd

from app.projetos_crawler import ProjetosCrawler
from app.proposicoes_crawler import ProposicoesCrawler

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/municipios")
def read_municipios():
    return [
        {"id": 9, "nome": "Ponta Grossa - PR"},
        {"id": 12, "nome": "União da Vitória - PR"},
    ]

@app.get("/proposicao/gerar-excel")
def generate_excel(id_municipio: int, tipo: str, data_inicio: str, data_final: str):
    crawler = ProposicoesCrawler(id_municipio=id_municipio, tipo=tipo, data_inicio=data_inicio, data_final=data_final)
    
    try:
        links = crawler.gera_links()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    dados = []

    for link in links:
       resposta = requests.get(link)
       pagina = BeautifulSoup(resposta.content, 'html.parser')
       dados = crawler.obter_dados(pagina)

    if not dados:
       raise HTTPException(status_code=404, detail="Nenhum dado encontrado")
    
    df = pd.DataFrame(dados)
    file_path = "/tmp/proposicao.xlsx"
    df.to_excel(file_path, index=False)
    
    return FileResponse(path=file_path, filename="proposicao.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.get("/proposicao/tipos")
def read_proposicao_tipos():
    return [
        {"id": 0, "nome": "Todos"},
        {"id": 1, "nome": "Indicação"},
        {"id": 2, "nome": "Requerimento"},
        {"id": 3, "nome": "Moção"},
        {"id": 4, "nome": "Resolução MD"},
        {"id": 5, "nome": "Portaria"},
    ]

@app.get("/projeto/gerar-excel")
def generate_excel(id_municipio: int, especie: str, data_inicio: str, data_final: str):
    crawler = ProjetosCrawler(id_municipio=id_municipio, especie=especie, data_inicio=data_inicio, data_final=data_final)
    
    try:
        links = crawler.gera_links()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    dados = []

    for link in links:
        resposta = requests.get(link)
        pagina = BeautifulSoup(resposta.content, 'html.parser')
        dados = crawler.obter_dados(pagina)

    if not dados:
        raise HTTPException(status_code=404, detail="Nenhum dado encontrado")
    
    df = pd.DataFrame(dados)
    file_path = "/tmp/projeto.xlsx"
    df.to_excel(file_path, index=False)
    
    return FileResponse(path=file_path, filename="projeto.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.get("/projeto/especies")
def read_projeto_especies():
    return [
        {"id": 0, "nome": "Todas"},
        {"id": 1, "nome": "Lei Ordinária"},
        {"id": 2, "nome": "Lei Complementar"},
        {"id": 3, "nome": "Decreto Legislativo"},
        {"id": 4, "nome": "Resolução"},
        {"id": 5, "nome": "Emenda a LOM"},
    ]