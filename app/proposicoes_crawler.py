# proposicoes_crawler.py

import requests
from bs4 import BeautifulSoup
import re
from requests.exceptions import HTTPError

class ProposicoesCrawler:

    def __init__(self, id_municipio, tipo="", data_inicio="", data_final=""):
        self.id_municipio = id_municipio
        self.tipo_proposicao = tipo
        self.data_inicio = data_inicio
        self.data_final = data_final
        self.dados_proposicoes = {
            "tipo_proposicao": [],
            "numero_proposicao": [],
            "data_proposicao": [],
            "situacao_proposicao": [],
            "assunto_proposicao": [],
            "autor_proposicao": [],
            "texto_proposicao": []
        }

    def __pagina_base(self):
        url_base = f'https://www.legislador.com.br/LegisladorWEB.ASP?WCI=ProposicaoConsulta&ID={self.id_municipio}&dtInicial={self.data_inicio}&dtFinal={self.data_final}&tpProposicao={self.tipo_proposicao}&'
        return url_base

    def __gera_args(self):
        resposta = requests.get(self.__pagina_base())
        if resposta.status_code != 200:
            raise HTTPError(f"Erro ao acessar a página: {resposta.status_code}")
        pagina = BeautifulSoup(resposta.content, 'html.parser')
        
        # Encontrar todos os elementos com a classe especificada
        proposicao_infos = pagina.find_all('a', {
            'class': 'btn btn-outline-secondary float-right d-flex justify-content-between align-items-center'})
        
        # Armazenar as informações em um array
        proposicoes = []
        for proposicao_info in proposicao_infos:
            proposicao_info_link = re.split('[()]', proposicao_info['onclick'])[1].split(',')

            cam_proposicao = proposicao_info_link[0]
            num_proposicao = int(proposicao_info_link[2])
            tipo_proposicao = proposicao_info_link[1]
            ano_proposicao = proposicao_info_link[3]

            proposicoes.append((cam_proposicao, tipo_proposicao, num_proposicao, ano_proposicao))
        
        return proposicoes

    def gera_links(self):
        links_proposicoes = []
        args_proposicoes = self.__gera_args()

        for args_proposicao in args_proposicoes:
            cam_proposicao, tipo_proposicao, num_proposicao, ano_proposicao = args_proposicao

            links_proposicoes.append(
                f'https://www.legislador.com.br/LegisladorWEB.ASP?WCI=ProposicaoTexto&ID={cam_proposicao}&TPProposicao={tipo_proposicao}&nrProposicao={num_proposicao}&aaProposicao={ano_proposicao}')

        return links_proposicoes

    def obter_dados(self, pagina):
        st_proposicao = len(pagina.find_all('dd', {'class': 'col-sm-9'}))

        self.dados_proposicoes["tipo_proposicao"].append(
            pagina.find('h5', {'class': 'card-title'}).get_text().split()[0])
        self.dados_proposicoes["numero_proposicao"].append(
            pagina.find('h5', {'class': 'card-title'}).get_text().split()[2])
        self.dados_proposicoes["data_proposicao"].append(
            pagina.find('h6', {'class': 'card-subtitle'}).get_text().split()[1])
        self.dados_proposicoes["situacao_proposicao"].append(
            pagina.find_all('dd', {'class': 'col-sm-9'})[2].get_text().split()[1] if st_proposicao == 5 else pagina.find_all('dd', {'class': 'col-sm-9'})[1].get_text())
        self.dados_proposicoes["assunto_proposicao"].append(
            pagina.find_all('dd', {'class': 'col-sm-9'})[3].get_text() if st_proposicao == 5 else pagina.find_all('dd', {'class': 'col-sm-9'})[2].get_text())
        self.dados_proposicoes["autor_proposicao"].append(
            pagina.find_all('dd', {'class': 'col-sm-9'})[4].get_text() if st_proposicao == 5 else pagina.find_all('dd', {'class': 'col-sm-9'})[3].get_text())
        self.dados_proposicoes["texto_proposicao"].append(re.sub(r"[\t\n\xa0\x93\x94\x95]"," ",pagina.find('p', {'class': 'card-text'}).get_text()))

        dados = self.dados_proposicoes
        return dados
