# Проект Flask API для экзамена DevOps

Этот проект реализует простой Flask REST API с базой данных PostgreSQL, разработанный для экзамена Lesta. Приложение упаковано в Docker и разворачивается с помощью CI/CD пайплайна на Jenkins.

## Содержание

- [API Эндпоинты](#api-эндпоинты)
- [Как запустить проект локально](#как-запустить-проект-локально)
- [Настройка CI/CD в Jenkins](#настройка-cicd-в-jenkins)
- [Как работает CI/CD](#как-работает-cicd)
- [Примеры API-запросов](#примеры-api-запросов)

---

## API Эндпоинты

Flask-приложение предоставляет следующие REST API-эндпоинты:

- **GET /ping**: Эндпоинт для проверки работоспособности API. Возвращает статус {"status": "ok"}.
  - **Ответ**: {"status": "ok"} (HTTP 200 OK)

- **POST /submit**: Отправляет пользовательские данные (имя и очки) в базу данных PostgreSQL. Ожидает JSON в теле запроса.
  - **Тело запроса (JSON)**:
    ```json
    {
      "name": "Roman",
      "score": 90
    }
    ```
  - **Ответ (успех)**:
    ```json
    {
      "id": 2,
      "message": "Result submitted successfully"
    }
    ```
    *(Точные значения `id` будут зависеть от вашей базы данных.)*
  - **Ответ при ошибке (отсутствуют данные)**:
    ```json
    {"error": "Missing 'name' or 'score' in request"}
    ```
    (HTTP 400 Bad Request)
  - **Ответ при ошибке (неверный формат данных)**:
    ```json
    {"error": "Invalid data format for 'score' or request body"}
    ```
    (HTTP 400 Bad Request)

- **GET /results**: Извлекает все записи из базы данных.
  - **Ответ**:
    ```json
    [
      {
        "id": 1,
        "name": "Kirill",
        "score": 88,
        "timestamp": "2025-05-30T10:25:40.000Z"
      },
      {
        "id": 2,
        "name": "Анна Смирнова",
        "score": 92,
        "timestamp": "2025-06-01T15:00:00.000Z"
      }
    ]
    ```
    (HTTP 200 OK)
    *(Содержимое будет зависеть от данных, которые были отправлены в базу данных.)*

---

## Как запустить проект локально

Для локального запуска проекта с использованием Docker Compose для разработки:

### Требования

- Установленный [Docker](https://docs.docker.com/engine/install/ubuntu/)
- Установленный [Docker Compose](https://docs.docker.com/compose/install/)

### Инструкция по запуску

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/Jaralet/flask-api-exam.git
   cd flask-api
   ```

2. **Создайте и настройте файл .env:**
   Скопируйте файл .env.example в .env. Откройте файл .env и заполните необходимые учетные данные для базы данных. Эти учетные данные будут использоваться как Flask-приложением, так и контейнером PostgreSQL.
   ```bash
   cp .env.example .env
   ```

3. **Запустите контейнеры с помощью docker-compose-local.yml:**
   ```bash
   docker compose -f docker-compose-local.yml up --build -d
   ```
   - --build: Этот флаг гарантирует, что Docker пересоберет образ сервиса web из вашего локального Dockerfile и исходного кода.
   - -d: Запускает контейнеры в отсоединенном режиме (в фоновом режиме).

4. **Миграции базы данных:**
   Скрипт entrypoint.sh внутри контейнера web автоматически обрабатывает flask db init, flask db migrate и flask db upgrade при первом запуске контейнера или если папка migrations отсутствует. Поэтому обычно вам не нужно запускать их вручную после docker compose up.

5. **Доступ к приложению:**
   Flask-приложение будет доступно по адресу http://localhost:5000.

---

## Настройка CI/CD в Jenkins

Этот проект использует Jenkins для автоматизации процессов CI/CD.

### Требования для Jenkins-сервера

- Установленный Jenkins.
- Установленный Docker на хост-машине Jenkins (чтобы Jenkins мог собирать образы).
- Установленный ssh-agent для выполнения команд на удаленном сервере.
- Настроенные учетные данные в Jenkins для доступа к Docker Hub и удаленному серверу.

### 1. Запуск Jenkins в Docker (пример)

Если Jenkins еще не установлен, вы можете запустить его в Docker-контейнере:

```bash
docker run -d -p 8080:8080 -p 50000:50000 --name jenkins-blueocean \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:latest
```

### 2. Дополнительные шаги в контейнере Jenkins (после первого запуска)

После запуска Jenkins-контейнера может потребоваться установка Docker CLI внутри него и настройка прав. Это необходимо, если Jenkinsfile будет выполнять команды Docker (например, для сборки образов).

1. **Получите начальный пароль администратора Jenkins:**
   ```bash
   docker exec jenkins-blueocean cat /var/jenkins_home/secrets/initialAdminPassword
   ```

2. **Подключитесь к контейнеру Jenkins как root:**
   ```bash
   docker exec -u 0 -it jenkins-blueocean /bin/bash
   ```

3. **Внутри контейнера, выполните следующие команды:**
   ```bash
   apt-get update && apt-get install -y docker.io sudo rsync pipx
   usermod -aG docker jenkins
   usermod -aG sudo jenkins
   exit
   ```

4. **Перезапустите контейнер Jenkins, чтобы изменения вступили в силу:**
   ```bash
   docker restart jenkins-blueocean
   ```

### 3. Настройка Pipeline Job в Jenkins UI

1. Перейдите в Jenkins UI (http://localhost:8080/) -> "Создать новый элемент".
2. Введите имя проекта (flask-api-pipeline), выберите "Pipeline", нажмите "ОК".
3. В секции "Pipeline" выберите: "Pipeline script from SCM".
4. В "SCM" выберите Git. Укажите URL вашего репозитория (https://github.com/Jaralet/flask-api-exam.git) и необходимые учетные данные (если репозиторий приватный).
5. Укажите "Script Path" как Jenkinsfile (это путь к файлу в корне вашего репозитория).
6. Сохраните Job.

### 4. Учетные данные в Jenkins

Для успешного выполнения пайплайна вам нужно настроить учетные данные в Jenkins:

- SSH-ключ для доступа к серверу развертывания
- Учетные данные Docker Hub

---

## Как работает CI/CD

Автоматизированный процесс развертывания приложения с помощью Jenkins Pipeline (Jenkinsfile) включает следующие этапы:

1. **Checkout**: Клонирование исходного кода проекта из Git-репозитория.
2. **Debug Workspace Contents**: (Только для отладки, может быть удален из финальной версии Jenkinsfile) Проверка содержимого рабочей директории Jenkins для подтверждения наличия всех файлов.
3. **Lint**: Выполнение статического анализа кода с помощью flake8 для проверки стиля и потенциальных ошибок.
4. **Build Docker Image**: Сборка Docker-образа Flask-приложения на основе Dockerfile из репозитория.
5. **Push to Docker Hub**: Публикация собранного Docker-образа в Docker Hub. Образ тегируется номером сборки Jenkins и тегом latest.
6. **Deploy to Remote Server**: Развертывание приложения на удаленной Linux-машине с использованием SSH-подключения. На удаленном сервере выполняется:
   - Обновление Docker-образа (docker compose pull).
   - Запуск/перезапуск контейнеров с помощью docker compose up -d.
7. **Verify Deployment**: Проверка работоспособности развернутого приложения путем отправки curl запроса к эндпоинту /ping. Если приложение не отвечает, выполняется несколько попыток с задержкой.

**Скриншот успешного завершения пайплайна**:

![Успешное завершение Jenkins Pipeline](https://i.ibb.co/W4st93KB/image.png)

---

## Примеры API-запросов

- **GET /ping**:
  ```bash
  curl http://localhost:5000/ping
  ```

- **POST /submit**:
  ```bash
  curl -X POST http://37.9.53.144:5000/submit \
    -H "Content-Type: application/json" \
    -d '{"name": "Roman", "score": 90}'
  ```

- **GET /results**:
  ```bash
  curl http://localhost:5000/results
  ```

