# Informed AI

## Overview

Informed AI is designed to help users get personalized updates about the weather in their location



## Code Setup

This project includes Docker configurations for an integrated execution environment which includes the frontend, backend, and Nginx modules.

### Initial Setup

1. **Fork the Repository**: Start by forking the repo to your GitHub account.
2. **Clone and Navigate**: Clone the forked repository to your local machine and navigate to the root folder of the project.

   ```bash
   git git@github.com:rahulrajesh23/informed-ai.git project_name
   cd project_name
   ```

3. **Install PostgreSQL and Redis**:
  - Setup PostgreSQL DB Server
  - Setup Redis Server
4. **Environment Setup**:
   - Set up a Python virtual environment:

     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
5. **Create .env file**:
   - Rename the `.env.template` file in the root directory and configure your API Key and other environment variables

6. **Docker Compose**:
   - Modify the `docker-compose.yml` file if necessary.
   - Run the Docker containers:

     ```bash
     docker-compose up -d
     ```

   This command starts the frontend React server, the backend FastAPI server, and configures Nginx to manage ports.

7. **Access the Application**:
   - The application should now be running and accessible via [http://localhost/app](http://localhost/app).

### Alternative Setup: Building Separately

If you prefer to build the frontend and backend separately using Docker, perform the following steps:

- Navigate to the respective directory (`frontend` or `backend`).
- Run the following command in each directory:

  ```bash
  docker-compose up -d
  
  ```
### Manual Build (Without Docker)

For developers preferring to manually set up the project without Docker:

1. **Frontend Setup**:
   - Navigate to the `/frontend` directory.
   - Install dependencies and start the server:

     ```bash
     npm install
     npm start
     ```

   - The frontend service will be available at [http://localhost:3000/informed](http://localhost:3000/informed).

2. **Backend Setup**:
   - Navigate to the `/backend` directory.
   - Install Python dependencies:

     ```bash
     pip install -r requirements.txt
     ```

   - Start the FastAPI server:

     ```bash
     uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
     ```

   - The backend service will be running at [http://localhost:8000](http://localhost:8000).

   - **Note**: If running the backend service manually, update the API paths in the frontend code. The Nginx configuration obfuscates the port number and adds `/api` to the backend APIs. For example, use `http://localhost:8000/api_name`.

### Deployment

- In your root folder, run the below cammands. Make sure to enter your DockerHub user and project details
  ```
  docker buildx build --platform linux/amd64 -t <dockerhub_username>/<frontend_project>:<tag> --push ./frontend
  docker buildx build --platform linux/amd64 -t <dockerhub_username>/<backend_project>:<tag> --push ./backend
  docker buildx build --platform linux/amd64 -t <dockerhub_username><nginx_project>:<tag> --push ./nginx
  ```
- Execute the 'server_build.sh' file on your host to fetch he containers and start the application. 

