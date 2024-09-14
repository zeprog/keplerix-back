
# Keplerix Backend
## How to Start the App
To start the Keplerix backend, follow these steps:
### 1. Clone the Repository
Make sure to clone the repository to your local machine:
```bash
git  clone <repository-url>
cd <repository-folder>
```
### 2. Ensure Docker and Docker Compose are installed
Make sure that you have Docker and Docker Compose installed on your system. You can verify their installations using the following commands:
```bash
docker  --version
docker-compose  --version
```
### 3. Start the App

**Option 1: Start in the Background**
To run the application in the background, use the following command:
```bash
docker-compose up -d
```
**Option 2: Start with Logs in the Foreground**
If you prefer to start the application with logs showing in the terminal, use:
```bash
docker-compose up
```
### 4. Stopping the Application
To stop the running containers, you can use the following command:
```bash
docker-compose down
```
### 5. Viewing Logs
To view the logs of the running application, use:
```bash
docker-compose logs -f
```