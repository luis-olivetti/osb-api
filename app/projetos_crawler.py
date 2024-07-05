# projetos_crawler.py

import logging
import requests
from bs4 import BeautifulSoup
import re
from requests.exceptions import HTTPError

class ProjetosCrawler:

    def __init__(self, id_municipio, especie="", data_inicio="", data_final=""):
        self.id_municipio = id_municipio
        self.especie = especie
        self.data_inicio = data_inicio
        self.data_final = data_final
        self.dados = {
            "especie": [],
            "numero": [],
            "data": [],
            "situacao": [],
            "assunto": [],
            "autor": [],
            "ementa": [],
            "texto": []
        }
        self.logger = logging.getLogger(__name__)

    def __pagina_base(self):
        url_base = f'https://www.legislador.com.br/LegisladorWEB.ASP?WCI=ProjetoConsulta&ID={self.id_municipio}&dtInicial={self.data_inicio}&dtFinal={self.data_final}&inEspecie={self.especie}&'
        return url_base

    def __gera_args(self):
        resposta = requests.get(self.__pagina_base())
        if resposta.status_code != 200:
            raise HTTPError(f"Erro ao acessar a página: {resposta.status_code}")
        pagina = BeautifulSoup(resposta.content, 'html.parser')

        pagina_infos = pagina.find_all('a', {
            'class': 'btn btn-outline-secondary float-right d-flex justify-content-between align-items-center'})
        
        projetos = []
        for pagina_info in pagina_infos:
            pagina_info_link = re.split('[()]', pagina_info['onclick'])[1].split(',')

            id = pagina_info_link[0]
            especie = pagina_info_link[1]
            numero = int(pagina_info_link[2])
            ano = pagina_info_link[3]

            projetos.append((id, especie, numero, ano))

        return projetos

    def gera_links(self):
        links = []
        argumentos = self.__gera_args()

        for argumentos in argumentos:
            id, especie, numero, ano = argumentos

            links.append(
                f'https://www.legislador.com.br/LegisladorWEB.ASP?WCI=ProjetoTexto&ID={id}&inEspecie={especie}&nrProjeto={numero}&aaProjeto={ano}')

        return links

    def obter_dados(self, pagina):
        try:
            #quantidade_objetos = len(pagina.find_all('dd', {'class': 'col-sm-9'}))
            #self.logger.info(f"Quantidade de dados: {quantidade_objetos}")

            titulo = pagina.find('h5', {'class': 'card-title'})
            if titulo:
                titulo_texto = titulo.get_text()
                match = re.search(r'(\d+)/(?:\d{4})', titulo_texto)
                if match:
                    numero = match.group(1)
                    especie = titulo_texto.replace(match.group(), '').strip()
                    self.logger.info(f"Espécie: {especie}, Número da lei: {numero}")
                else:
                    especie = "Espécie não encontrada"
                    numero = "Número não encontrado"
                    self.logger.error("Número da lei não encontrado")
            else:
                especie = "Espécie não encontrada"
                numero = "Número não encontrado"
                self.logger.error("Elemento <h5> com classe 'card-title' não encontrado")

            self.dados["especie"].append(especie)
            self.dados["numero"].append(numero)
            self.dados["data"].append(pagina.find('h6', {'class': 'card-subtitle'}).get_text().split()[1])

            # Determinando posição dos dados dependendo da quantidade de proposições
            # Obrigo a pegar o mesmo índice para todos os dados
            situacao_idx = 0# if st_proposicao == 5 else 2
            assunto_idx = 3# if st_proposicao == 5 else 2
            autor_idx = 4# if st_proposicao == 5 else 3

            self.dados["situacao"].append(pagina.find_all('dd', {'class': 'col-sm-9'})[situacao_idx].get_text())
            self.dados["assunto"].append(pagina.find_all('dd', {'class': 'col-sm-9'})[assunto_idx].get_text())
            self.dados["autor"].append(pagina.find_all('dd', {'class': 'col-sm-9'})[autor_idx].get_text())

            # Extraindo texto da ementa
            ementa = pagina.find('div', {'class': 'card-header'}, text='Ementa')
            if ementa:
                ementa_texto = ementa.find_next_sibling('div', {'class': 'card-body'}).find('p', {'class': 'card-text'}).get_text().strip()
            else:
                ementa_texto = "Ementa não encontrada"

            # Extraindo texto principal
            texto = pagina.find('div', {'class': 'card-header'}, text='Texto')
            if texto:
                texto_texto = texto.find_next_sibling('div', {'class': 'card-body'}).find('p', {'class': 'card-text'}).get_text().strip()
            else:
                texto_texto = "Texto não encontrado"

            self.dados["ementa"].append(ementa_texto)
            self.dados["texto"].append(texto_texto)

        except Exception as e:
            self.logger.error(f"Erro ao extrair dados da página: {e}")

        return self.dados