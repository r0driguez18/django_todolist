# Django ToDoList

## Como executar (dev)
a) Clone de repositório GitHub:
```bash
git clone https://github.com/zeguimoko/django_todolist.git
```
b) Entrar na pasta do projeto `django_todolist`:
```bash
cd django_todolist
```
c) Criar arquivo `.env` com as variáveis de ambiente:
```bash
cp .env.example .env
```

## [Opção 1] - Executar com Python Virtual Environment
1 - Criar ambiente virtual:
```bash
python -m venv venv
```
2 - Ativar ambiente virtual:
- Linux/Mac:
```bash
source venv/bin/activate
```
- Windows (Command Prompt):
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\activate
```
3 - Instalar dependências:
```bash
pip install -r requirements.txt
```
4 - Executar comando `migrate`, para criar tabelas:
```bash
python todolist_project/manage.py migrate
```
5 - Executar comando `createsuperuser`, para criar superuser:
```bash
python todolist_project/manage.py createsuperuser
```
6 - Executar comando `runserver` para executar a aplicação:
```bash
python todolist_project/manage.py runserver 0.0.0.0:8000
```

## [Opção 2] -  Ou Executar com Docker Compose (opcional)

1 - Criar imagem e Iniciar a aplicação com Docker Compose:
```bash
docker compose up -d --build
```
2 - Parar a aplicação com Docker Compose e remover containers orphans:
```bash
docker compose down --remove-orphans
```

## [Opção 3] - Ou Docker RUN (opcional)

1 - Criar imagem
```bash
docker build -t django_todolist:0.0.0 .
```

2 - Executar o container (iniciar a aplicação):
- Especifica o nome do container;
- Mapeia a porta 8000 do host para a 8000 do container;
- Mapeia o VOLUME no diretório atual para a pasta `/app` do container;
- Carrega as variáveis de ambiente do arquivo `.env`.

#### Platformas:

- Linux/Mac:
```bash
docker run --rm --name django_todolist -p 8000:8000 -v $(pwd):/app --env-file .env django_todolist:0.0.0
```
- Windows (Command Prompt):
```bash
docker run --rm --name django_todolist -p 8000:8000 -v %cd%:/app --env-file .env django_todolist:0.0.0
```

- Windows (PowerShell):
```bash
docker run --rm --name django_todolist -p 8000:8000 -v ${PWD}:/app --env-file .env django_todolist:0.0.0
```

## Comando de Suporte ao Docker:

a) Criar superuser:
```bash
docker exec -it django_todolist python todolist_project/manage.py createsuperuser
```

b) Ver logs do container `django_todolist`
```bash
docker logs -f django_todolist
```
___
## Segurança (ASVS-alinhado)
- Controlo de acesso por proprietário do recurso (IDOR mitigado).
- Cookies HttpOnly/Secure em produção; `DEBUG=False` em prod.
- Escape em templates e CSRF ativo por defeito.
```


