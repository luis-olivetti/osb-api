# OSB-API

Este projeto é uma API Python que utiliza crawlers para extrair dados legislativos e transformá-los em uma planilha Excel para download. Inicialmente, atende os municípios de União da Vitória - PR e Ponta Grossa - PR.

## Inicialização da Aplicação

Instale as depêndencias do projeto com o seguinte comando:
```bash
$ pip install --no-cache-dir -r requirements.txt
```

Utilize o uvicorn para iniciar a aplicação FastAPI. No terminal, navegue até a raíz do projeto e execute:

```bash
$ uvicorn app.main:app --reload
```
- main é o nome do arquivo (sem a extensão .py).
- app é o nome da instância do FastAPI no arquivo.
- --reload é uma opção que recarrega o servidor automaticamente quando você faz alterações no código. Isso é útil para desenvolvimento.

## Utilização com Docker

Para construir e executar a aplicação utilizando Docker, siga os seguintes passos:

1. Construir a imagem Docker:
```bash
$ docker build -t osb_api_image .
```

2. Executar o contêiner Docker:
```bash
$ docker run -d -p 8000:8000 --name osb_api_container osb_api_image
```

## Referências e agradecimentos

Esta API foi criada com base no repositório [Observatório](https://github.com/oliver-rafael/observatorio) do Rafael Silva, que desenvolveu a extração de Proposições. Agradecemos ao autor.