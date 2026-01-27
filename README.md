# Django ToDoList

## Como executar (dev)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python todolist_project/manage.py migrate
python todolist_project/manage.py createsuperuser
python todolist_project/manage.py runserver 0.0.0.0:8000
```

## Docker (opcional)
```bash
docker build -t django-todolist .
docker run --rm -p 8000:8000 --env-file .env django-todolist
```

## Segurança (ASVS-alinhado)
- Controlo de acesso por proprietário do recurso (IDOR mitigado).
- Cookies HttpOnly/Secure em produção; `DEBUG=False` em prod.
- Escape em templates e CSRF ativo por defeito.
```
