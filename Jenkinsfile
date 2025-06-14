pipeline {
    agent any

    parameters {
        string(name: 'REMOTE_HOST_IP', defaultValue: '37.9.53.144', description: 'Enter the IP address of the remote host where the application should be deployed')
        string(name: 'REMOTE_USER', defaultValue: 'ubuntu', description: 'Username for SSH connection to the remote host')
    }

    environment {
        IMAGE_NAME = 'jaralet/flask-api'
        REMOTE_DIR = 'flask-api'
        DOCKER_CREDENTIALS_ID = 'docker-hub-credentials'
        SSH_CREDENTIALS_ID = 'remote-server-ssh-key'
        SECRETS_FILE_ID = 'flask-app-env-file'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Debug Workspace Contents') {
            steps {
                script {
                    echo "Listing contents of workspace after checkout:"
                    sh 'ls -R'
                    echo "Checking of migrations directory exists and it contents"
                    sh 'ls -R migrations || echo "migrations directory not found or empty"'
                }
            }
        }

        stage('Lint') {
            steps {
                script {
                    sh """
                    docker run --rm \\
                        -v "\$(pwd):/app" \\
                        -w /app \\
                        python:3.10-slim \\
                        bash -c "pip install --no-cache-dir flake8 && flake8 . || true"
                    """
                }
            }
        }

        stage('Confirm Deployment Parameters') {
            steps {
                script {
                    input message: "Review parameters and confirm deployment to ${params.REMOTE_HOST_IP}. Proceed?", ok: 'Proceed'
                }
            }
        }

        stage('Install Docker and Docker Compose on Remote Server') {
            steps {
                sshagent([SSH_CREDENTIALS_ID]) {
                    script {
                        def remoteHost = "${params.REMOTE_USER}@${params.REMOTE_HOST_IP}"
                        sh """
                        echo "Checking and installing Docker and Docker Compose on the remote server..."

                        ssh -o StrictHostKeyChecking=no ${remoteHost} '
                            if ! command -v docker &> /dev/null; then
                                echo "Installing Docker..."
                                sudo apt-get update && \\
                                sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common && \\
                                curl -fsSL https://get.docker.com -o get-docker.sh && \\
                                sudo sh get-docker.sh && \\
                                sudo systemctl start docker && \\
                                sudo systemctl enable docker
                            else
                                echo "Docker is already installed"
                            fi

                            if ! command -v docker-compose &> /dev/null; then
                                echo "Installing Docker Compose..."
                                sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose && \\
                                sudo chmod +x /usr/local/bin/docker-compose && \\
                                sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
                            else
                                echo "Docker Compose is already installed"
                            fi
                        '
                        """
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${IMAGE_NAME}:${BUILD_NUMBER}")
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', DOCKER_CREDENTIALS_ID) {
                        dockerImage.push("${BUILD_NUMBER}")
                        dockerImage.push("latest")
                    }
                }
            }
        }

        stage('Deploy to Remote Server') {
            steps {
                sshagent([SSH_CREDENTIALS_ID]) {
                    withCredentials([file(credentialsId: SECRETS_FILE_ID, variable: 'SECRET_FILE_PATH')]) {
                        script {
                            def remoteHost = "${params.REMOTE_USER}@${params.REMOTE_HOST_IP}"
                            sh """
                            echo "Copying necessary files and deploying to the server..."

                            ssh -o StrictHostKeyChecking=no ${remoteHost} 'mkdir -p ${REMOTE_DIR}'
                            ssh -o StrictHostKeyChecking=no ${remoteHost} 'rm -rf ${REMOTE_DIR}/*'

                            rsync -avz --delete -e "ssh -o StrictHostKeyChecking=no" ./docker-compose.yml ${remoteHost}:${REMOTE_DIR}/
                            rsync -avz --delete -e "ssh -o StrictHostKeyChecking=no" ${SECRET_FILE_PATH} ${remoteHost}:${REMOTE_DIR}/.env

                            ssh ${remoteHost} '
                                cd ${REMOTE_DIR} && \\
                                sudo docker-compose down || true && \\
                                sudo docker-compose pull && \\
                                sudo docker-compose up -d --remove-orphans
                            '
                            """
                        }
                    }
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                script {
                    echo "Checking application health at http://${REMOTE_HOST_IP}:5000/ping"
                    timeout(time: 2, unit: 'MINUTES') {
                        def maxRetries = 10
                        def delayBetweenRetries = 10

                        for (int i = 0; i < maxRetries; i++) {
                            try {
                                sh "curl --fail --silent http://${REMOTE_HOST_IP}:5000/ping"
                                echo "Application health check successful!"
                                break
                            } catch (e) {
                                if (i < maxRetries - 1) {
                                    echo "Application health check failed (attempt ${i + 1}/${maxRetries}). Retrying in ${delayBetweenRetries} seconds..."
                                    sleep delayBetweenRetries
                                } else {
                                    error "Application health check failed after ${maxRetries} attempts."
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}