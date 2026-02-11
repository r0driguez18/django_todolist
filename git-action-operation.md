# Guia de Sessão – CI/CD com GitHub Actions (Docker Hub + Deploy via SSH)

Este documento serve como **suporte prático** para a sessão de CI/CD, mostrando como:

1. Fazer **CI**: build e push de imagem Docker para o Docker Hub
2. Fazer **CD**: ligar numa VM via SSH, fazer `docker compose pull` e atualizar a aplicação com `docker compose up -d`

> **Evento de trigger:** publicação de uma **Release** no GitHub.

---

## Índice

1. [Objetivo](#1-objetivo)
2. [Conceitos: CI vs CD](#2-conceitos-ci-vs-cd)
3. [Arquitetura do fluxo](#3-arquitetura-do-fluxo)
4. [Pré-requisitos](#4-pré-requisitos)
5. [Estrutura do workflow](#5-estrutura-do-workflow)
6. [Configurar Secrets no GitHub](#6-configurar-secrets-no-github)
7. [Preparação na VM (servidor)](#7-preparação-na-vm-servidor)
8. [Workflow final (CI + CD)](#8-workflow-final-ci--cd)
9. [Como executar (criar Release)](#9-como-executar-criar-release)
10. [Como validar o deploy](#10-como-validar-o-deploy)
11. [Boas práticas e segurança](#11-boas-práticas-e-segurança)
12. [Documentação útil](#12-documentação-útil)

---

## 1) Objetivo

Automatizar o ciclo **Build → Publish → Deploy** sempre que uma **Release** for publicada:

* **CI**: build da imagem Docker e push para Docker Hub
* **CD**: deploy automatizado numa VM via SSH, puxando a nova imagem e reiniciando os serviços

---

## 2) Conceitos: CI vs CD

### CI (Continuous Integration)

Processo automático que valida e prepara entregas, por exemplo:

* build
* testes
* análise de qualidade
* build e push de imagens

### CD (Continuous Delivery)

Processo automático que coloca a versão em ambiente (ex.: staging/prod):

* pull da imagem
* atualização do `docker compose`
* reinício controlado dos serviços

---

## 3) Arquitetura do fluxo

```text
GitHub Release (published)
        |
        v
GitHub Actions (CI)
  - build image
  - push Docker Hub
        |
        v
GitHub Actions (CD)
  - SSH para VM
  - docker compose pull
  - docker compose up -d
```

---

## 4) Pré-requisitos

### No GitHub

* Repositório com:

  * `Dockerfile`
  * workflow em `.github/workflows/...yml`
* Conta Docker Hub (para publicar imagens)
* Secrets configurados

### Na VM (Servidor)

* Docker instalado
* Docker Compose v2 instalado (`docker compose version`)
* Pasta com `docker-compose.yml` e configuração da aplicação
* O compose deve referenciar a imagem do Docker Hub (ex.: `ejst/django_todolist:latest`)

---

## 5) Estrutura do workflow

O workflow tem **2 jobs**:

### Job 1 — `build-and-push-ci`

* Checkout do código
* Setup Buildx
* Login no Docker Hub
* Build e Push da imagem (tags: `latest` e tag da release)

### Job 2 — `deploy-to-server-cd`

* Depende do job 1 (`needs`)
* Prepara chave SSH (Base64 → ficheiro)
* Liga por SSH na VM e executa:

  * `docker compose pull`
  * `docker compose up -d --remove-orphans`
  * `docker compose ps`
  * `docker image prune -f`

---

## 6) Configurar Secrets no GitHub

Em: **Settings → Secrets and variables → Actions**

### Docker Hub

* `DOCKERHUB_USERNAME` → teu utilizador do Docker Hub
* `DOCKERHUB_TOKEN` → token/pat do Docker Hub (recomendado em vez de password)

### VM / SSH

* `DO_HOST` → IP/hostname da VM
* `DO_USER` → user SSH (ex.: `root` ou `deploy`)
* `DO_APP_PATH` → pasta onde está o `docker-compose.yml` na VM
  Ex.: `/opt/devops`
* `DO_SSH_PRIVATE_KEY_B64` → chave privada em Base64 (para evitar problemas de quebras de linha)

#### Como gerar e converter a chave privada para Base64
1) Gerar uma nova chave (guarda como `~/.ssh/id_rsa_github`):
```bash
ssh-keygen -t rsa -b 4096 -C "github-deploy" -f ~/.ssh/id_rsa_github
```
2) Converter para Base64 e copiar (macOS / Linux / WSL / Windows com Git Bash):
```bash
base64 -i ~/.ssh/id_rsa_github
```
3) Converter para Base64 no Windows (PowerShell):
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("$env:USERPROFILE\\.ssh\\id_rsa_github"))
```
   - Se estiver em Windows mas a usar Git Bash ou WSL, pode usar o mesmo comando do passo 2 (`base64 -i ~/.ssh/id_rsa_github`).
4) Colar a saída no secret `DO_SSH_PRIVATE_KEY_B64`. Guarde o público (`~/.ssh/id_rsa_github.pub`) na VM em `~/.ssh/authorized_keys`.

---

## 7) Preparação na VM (servidor)

### 7.1 Confirmar Docker + Compose

Na VM:

```bash
docker --version
docker compose version
```

### 7.2 Pasta da aplicação

Exemplo:

```bash
mkdir -p /opt/devops
cd /opt/devops
```

Deve conter `docker-compose.yml`.

### 7.3 Utilizar o ficheiro `docker-compose.yml` na raiz do projeto.

---

## 8) Workflow final (CI + CD)
> Copiar o conteúdo abaixo para o ficheiro `.github/workflows/dockerhub-publish.yml`
```yaml
name: Build and Publish Docker Image (on Release)

on:
  release:
    types: [published]

jobs:
  build-and-push-ci:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to DockerHub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and Push Docker Image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile
          push: true
          platforms: linux/amd64
          tags: |
            ejst/django_todolist:latest
            ejst/django_todolist:${{ github.event.release.tag_name }}
          cache-from: type=registry,ref=ejst/django_todolist:buildcache
          cache-to: type=registry,ref=ejst/django_todolist:buildcache,mode=max
    
  deploy-to-server-cd:
    runs-on: ubuntu-latest
    needs: build-and-push-ci

    steps:
      - name: Prepare SSH key
        run: |
            mkdir -p ~/.ssh
            echo "${{ secrets.DO_SSH_PRIVATE_KEY_B64 }}" | base64 -d > ~/.ssh/id_key
            chmod 600 ~/.ssh/id_key
      - name: Deploy via SSH (docker compose pull && up -d)
        run: |
            ssh -i ~/.ssh/id_key -o StrictHostKeyChecking=no ${{ secrets.DO_USER }}@${{ secrets.DO_HOST }} << 'EOF'
            set -euo pipefail
            cd "${{ secrets.DO_APP_PATH }}"
            docker compose pull
            docker compose up -d --remove-orphans
            docker compose ps
            docker image prune -f
            EOF
```

---

## 9) Como executar (criar Release)

1. Fazer push do código para o GitHub
2. Criar uma **Release**:

   * GitHub → **Releases** → **Draft a new release**
   * Tag (ex.: `v1.0.0`)
   * **Publish release**

Ao publicar, o GitHub Actions dispara automaticamente.

---

## 10) Como validar o deploy

### 10.1 No GitHub Actions

* Ver workflow “verde”
* Confirmar logs do job `deploy-to-server-cd`

### 10.2 Na VM

```bash
cd /opt/devops
docker compose ps
docker compose logs -f --tail=100
```

### 10.3 No browser

Aceder à app:

```text
http://<IP_DA_VM>:8000
```

---

## 11) Boas práticas e segurança

* NÃO utilizar SSH para CI/CD para ambiente de PRODUÇÃO. Este exemplo foi utilizado apenas para demonstração, devido a limitação de ferramentas utilizadas, comcretamente o Portainer Community.
* Usar **chave SSH dedicada** para CI/CD (não a tua pessoal)
* Preferir user `deploy` com permissões limitadas (evitar root em produção)

---

## 12) Documentação útil

* GitHub Actions:
  [https://docs.github.com/actions](https://docs.github.com/actions)
* Docker Buildx:
  [https://docs.docker.com/build/buildx/](https://docs.docker.com/build/buildx/)
* docker/build-push-action:
  [https://github.com/docker/build-push-action](https://github.com/docker/build-push-action)
* docker/login-action:
  [https://github.com/docker/login-action](https://github.com/docker/login-action)
* SSH (OpenSSH):
  [https://www.openssh.com/manual.html](https://www.openssh.com/manual.html)
* Docker Compose:
  [https://docs.docker.com/compose/](https://docs.docker.com/compose/)
