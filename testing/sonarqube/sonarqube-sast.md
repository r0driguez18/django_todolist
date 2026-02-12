# SonarQube SAST (Guia Prático)

Guia rápido para levantar o **SonarQube + Postgres via Docker Compose** (arquivo `testing/sonarqube/docker-compose.yml`) e executar uma análise **SAST** com o `sonar-scanner` em contêiner. Tudo em português e orientado a passos.

---

## Índice

1. [O que é SonarQube e SAST](#1️⃣-o-que-é-sonarqube-e-sast)
2. [Componentes do docker-compose](#2️⃣-componentes-do-docker-compose)
3. [Pré-requisitos](#3️⃣-pré-requisitos)
4. [Preparar variáveis (.env)](#4️⃣-preparar-variáveis-env)
5. [Subir o stack com Docker Compose](#5️⃣-subir-o-stack-com-docker-compose)
6. [Primeiro acesso e configuração inicial](#6️⃣-primeiro-acesso-e-configuração-inicial)
7. [Criar projeto](#7️⃣-criar-projeto)
8. [Executar análise SAST com sonar-scanner (Docker)](#8️⃣-executar-análise-sast-com-sonar-scanner-docker)
9. [Parar, limpar e recomeçar](#9️⃣-parar-limpar-e-recomeçar)
10. [Resolução de problemas](#🔟-resolução-de-problemas)
11. [Referências oficiais](#1️⃣1️⃣-referências-oficiais)

---

## 1️⃣ O que é SonarQube e SAST

* **SAST** (Static Application Security Testing): análise de código-fonte sem executar a aplicação, detectando vulnerabilidades cedo no ciclo de desenvolvimento.
* **SonarQube**: plataforma para inspeção contínua de qualidade e segurança de código (bugs, code smells, vulnerabilidades, hotspots de segurança).

Objetivo deste guia: levantar o SonarQube localmente com Postgres e executar uma análise SAST em projeto `django-todolist` usando o `sonar-scanner` em contêiner.

---

## 2️⃣ Componentes do docker-compose

Arquivo: `testing/sonarqube/docker-compose.yml`

Serviços definidos:

* **sonarqube**
  * Imagem: `sonarqube:26.1.0.118079-community`
  * Porta exposta: `9000:9000`
  * Variáveis de BD: `SONAR_JDBC_URL`, `SONAR_JDBC_USERNAME`, `SONAR_JDBC_PASSWORD`. Estas variáveis precisam ser definidas no ficheiro `.env`, cso contrário, o Docker Compose utiliza os defaults definidas no fichero `docker-compose.yml`.
  * Volumes: `bca-sonarqube_data`, `bca-sonarqube_extensions`, `bca-sonarqube_logs`
  * Rede externa: `web-app-network` (não é criada pelo Compose, precisamos criar antes se ainda não existir: `docker network create web-app-network`)

* **bca-postgres18**
  * Imagem: `postgres:18.1`
  * Variáveis: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
  * Volume: `bca-postgres18_data`

**Rede externa**: `web-app-network` (não é criada pelo Compose, precisamos criar antes se ainda não existir).

---

## 3️⃣ Pré-requisitos

* Docker e Docker Compose instalados e funcionais.
* Porta **9000** livre no host. caso contrário, muda a porta no `docker-compose.yml` (`"<porta_nova>:9000"`) e atualiza/adicionar o ENV `SONAR_HOST_URL=http://localhost:<porta_nova>`.
* Espaço em disco para os volumes persistentes.

---

## 4️⃣ Preparar variáveis (.env)

O `docker-compose.yml` aceita variáveis com *defaults*, mas é boa prática definir um ficheiro `.env` na mesma pasta (`testing/sonarqube/.env`).

> Exemplo disponibilizado no ficheiro `.env.example` nesta mesma pasta. Copia o conteúdo para `testing/sonarqube/.env` antes de subir o stack (docker-compose.yml). Ajusta as passwords se necessário.

---

## 5️⃣ Subir o stack com Docker Compose

1. **Criar a rede externa (se ainda não existir):**
   ```bash
   docker network create web-app-network
   ```

2. **Subir os serviços** usando o compose da pasta `testing/sonarqube`:
    * Mover para a pasta `testing/sonarqube`:
   ```bash
   cd testing/sonarqube
   ```
    * Subir o stack com Docker Compose:
   ```bash
   docker compose up -d
   ```

3. **Verificar estado dos containers**:
Deve aparecer os containers `bca-postgres18` e `bca-sonarqube`.
   ```bash
   docker compose ps
   ```
   **PostgreSQL**: Deve aparecer logs do container --> `database system is ready to accept connections`
   ```bash
   docker logs --follow bca-postgres18
   ```
   **SonarQube**: Deve aparecer logs do container --> `SonarQube is operational`.
   ```bash
   docker logs --follow bca-sonarqube
   ```

4. **Acessar a UI**: abrir `http://localhost:9000` no navegador.\
    Se tudo estiver certo, deve aparecer a UI do SonarQube.
---

## 6️⃣ Primeiro acesso e configuração inicial

1. Login inicial: `admin` / `admin`.
2. O SonarQube solicita alterar a password — define uma nova senha segura.

---

## 7️⃣ Criar projeto

1. No menu lateral, escolhe **Projects** e de seguida clicar em **Add Project**.
2. Escolha a forma que quer criar o projeto: **Create a local project**.
3. Dá um nome e `Project Key` como: `django-todolist`.
4. Indicar o branch a ser analisado: `main`.
5. Clicar em **Next**.
6. Configurar os critérios de como é considerado o codigo como NOVO, permitindo que você se concentre nas alterações mais recentes do seu projeto.
    * para esta demostração escolhemos o `default`.
7. Clicar em **Create Project**.
8. Escolher o "Analysis Method", clicando na opção “Locally”.
9. **Gerar token:** definir o nome do token e a data de expiração.
    * clicar em **Generate** e copiar o token gerado.
    * clicar em continue.
    > Precisamos do **Project Key** e do **Token** para a análise SAST.
10. Escolher o **Tecnologia** utilizada no projeto: `Python`.
    * aprsenta CLI para do Scanner `pysonar` para projetos Python: 
        ```bash
        python3 -m pip install pysonar
        ```
    * apresenta o CLI para o Scanner `sonar-scanner` para projeto python:
        > deve ser executado na pasta RAIZ do projeto.
        > copiar o comando e executar a analise estática. Entretanto, proximos scanaers serao executados usando container do Scanner:
        ```bash
        pysonar \
        --sonar-host-url=http://localhost:9000 \
        --sonar-token=[TOKEN] \
        --sonar-project-key=django-todolist
        ```
11. Se tudo correr bem, deve aparecer na UI do SonarQube o resultado da análise.

---

## 8️⃣ Executar análise SAST com sonar-scanner (Docker)

Vamos usar o contêiner oficial `sonarsource/sonar-scanner-cli` para evitar instalação local.

### 8.1 (Opcional) Rodar o scanner a partir do diretório do código
SonarScanner é a ferramenta de linha de comando que coleta código-fonte + metadados do projeto, calcula métricas estáticas e envia os resultados para um servidor SonarQube/SonarCloud. O SonarScanner Funciona como “cliente” do Sonar.
* Alterar o valor SONAR_TOKEN para o token gerado na criação do projeto e executar o scanner a partir do diretório do projeto.
* Para windows: alterar o volume para `${PWD}:/usr/src` e para `${PWD}/.git:/usr/src/.git`.
    ```bash
    docker run --rm --network web-app-network \
        -e SONAR_HOST_URL="http://bca-sonarqube:9000" \
        -e SONAR_SCANNER_OPTS="\
        -Dsonar.projectKey=django-todolist \
        -Dsonar.sources=. \
        -Dsonar.python.version=3.12 \
        -Dsonar.scm.provider=git \
        -Dsonar.scm.disabled=false" \
        -e SONAR_TOKEN="[PASSAR TOKEN AQUI]" \
        -v "$(pwd):/usr/src" \
        -v "$(pwd)/.git:/usr/src/.git" \
        --platform='linux/amd64' \
        sonarsource/sonar-scanner-cli
    ```

Notas importantes:
* Executa o comando **dentro da pasta do projeto** que queres analisar.
* A flag `--network web-app-network` permite o scanner comunicar com o contêiner `sonarqube` pelo nome `bca-sonarqube:9000`.
* Ajusta a versão de Python ou adiciona outras linguagens via propriedades `-Dsonar.language` quando aplicável.

### 8.2 Ver resultados

* Acompanhar o log do scanner: sairá no terminal.
* Abrir `http://localhost:9000/projects` e selecionar o projeto para ver issues, métricas e cobertura.

---

## 9️⃣ Parar, limpar e recomeçar

* Parar serviços:
  ```bash
  docker compose -f testing/sonarqube/docker-compose.yml down
  ```

* Parar e remover volumes (ATENCAO: dados e histórico serão apagados):
  ```bash
  docker compose -f testing/sonarqube/docker-compose.yml down -v
  ```

* Remover rede se não for mais usada:
  ```bash
  docker network rm web-app-network
  ```

---

## 🔟 Resolução de problemas

* **Porta 9000 ocupada**: muda para outra porta no `docker-compose.yml` (`"<porta_nova>:9000"`) e atualiza o `SONAR_HOST_URL`.
* **Rede não encontrada**: cria `web-app-network` antes de subir o stack.
* **Token inválido / 401**: gere novo token e exporte novamente `SONAR_TOKEN`.
* **Erro de BD**: confirma credenciais no `.env` e se o volume `bca-postgres16_data` não está corrompido (remover volume para resetar).
* **Scanner não encontra o host**: assegura que o `SONAR_HOST_URL` aponta para o host correto (dentro da rede do Docker pode usar `http://bca-sonarqube:9000`).

---

## 1️⃣1️⃣ Referências oficiais

* SonarQube: https://docs.sonarsource.com/sonarqube/latest/
* Scanner CLI: https://docs.sonarsource.com/sonarqube/latest/analysis/scan/sonarscanner-for-cli/
* Propriedades do Scanner: https://docs.sonarsource.com/sonarqube/latest/analysis/parameters/
* Docker Hub SonarQube: https://hub.docker.com/_/sonarqube

---

Este guia serve como apoio rápido para levantar o SonarQube local e executar SAST em projetos com Docker, alinhado com o ficheiro `testing/sonarqube/docker-compose.yml` deste repositório.
