# osb-api

Utilize o uvicorn para iniciar a aplicação FastAPI. No terminal, navegue até a raíz do projeto e execute:

```bash
$ uvicorn app.main:app --reload
```
- main é o nome do arquivo (sem a extensão .py).
- app é o nome da instância do FastAPI no arquivo.
- --reload é uma opção que recarrega o servidor automaticamente quando você faz alterações no código. Isso é útil para desenvolvimento.

```bash
$ docker build -t osb_api_image .
$ docker run -d -p 8000:8000 --name osb_api_container osb_api_image
```