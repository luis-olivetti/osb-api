# projetos_crawler.py

import logging
import requests
from bs4 import BeautifulSoup
import re
from requests.exceptions import HTTPError

class ProjetosCrawler:

    def __init__(self, especie="", data_inicio="", data_final=""):
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
        url_base = f'https://www.legislador.com.br/LegisladorWEB.ASP?WCI=ProjetoConsulta&ID=9&dtInicial={self.data_inicio}&dtFinal={self.data_final}&inEspecie={self.especie}&'
        return url_base

    def __gera_args(self):
        resposta = requests.get(self.__pagina_base())
        if resposta.status_code != 200:
            raise HTTPError(f"Erro ao acessar a página: {resposta.status_code}")
        pagina = BeautifulSoup(resposta.content, 'html.parser')
        pagina_info = pagina.find('a', {
            'class': 'btn btn-outline-secondary float-right d-flex justify-content-between align-items-center'})
        pagina_info_link = re.split('[()]', pagina_info['onclick'])[1].split(',')

        id = pagina_info_link[0]
        especie = pagina_info_link[1]
        numero = int(pagina_info_link[2])
        ano = pagina_info_link[3]

        return id, especie, numero, ano

    def gera_links(self):
        links = []
        argumentos = self.__gera_args()

        for projeto in range(argumentos[2]):
            links.append(
                f'https://www.legislador.com.br/LegisladorWEB.ASP?WCI=ProjetoTexto&ID={argumentos[0]}&inEspecie={argumentos[1]}&nrProjeto={argumentos[2] - projeto}&aaProjeto={argumentos[3]}')

        return links

    def obter_dados(self, pagina):
        try:
            # Contando a quantidade de elementos 'dd' com a classe 'col-sm-9'
            st_proposicao = len(pagina.find_all('dd', {'class': 'col-sm-9'}))

            # Adicionando logs para identificar o número de proposições na página
            self.logger.info(f"Quantidade de dados: {st_proposicao}")

            # Extraindo número da lei se houver 9 proposições
            #if st_proposicao == 9:
            #    numero_match = re.search(r'\b(\d+)/\d{4}\b', pagina.find('h5', {'class': 'card-title'}).get_text())
            #    numero = numero_match.group(1) if numero_match else None
            #    self.logger.info(f"Número da lei: {numero}")

            # Adicionando dados ao dicionário
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

            # Adicionando dados ao dicionário
            self.dados["especie"].append(especie)
            self.dados["numero"].append(numero)
            self.dados["data"].append(pagina.find('h6', {'class': 'card-subtitle'}).get_text().split()[1])

            # Determinando posição dos dados dependendo da quantidade de proposições
            #obrigo a pegar o mesmo indice para todos os dados
            situacao_idx = 0# if st_proposicao == 5 else 2
            assunto_idx = 3# if st_proposicao == 5 else 2
            autor_idx = 4# if st_proposicao == 5 else 3

            self.dados["situacao"].append(pagina.find_all('dd', {'class': 'col-sm-9'})[situacao_idx].get_text())
            self.dados["assunto"].append(pagina.find_all('dd', {'class': 'col-sm-9'})[assunto_idx].get_text())
            self.dados["autor"].append(pagina.find_all('dd', {'class': 'col-sm-9'})[autor_idx].get_text())
            #self.dados["texto"].append(re.sub(r"[\t\n\xa0\x93\x94\x95]", " ", pagina.find('p', {'class': 'card-text'}).get_text()))

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

            # Adicionando dados ao dicionário
            self.dados["ementa"].append(ementa_texto)
            self.dados["texto"].append(texto_texto)

        except Exception as e:
            self.logger.error(f"Erro ao extrair dados da página: {e}")

        return self.dados