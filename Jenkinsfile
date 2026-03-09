pipeline {
    agent any

    environment {
        APP_NAME    = 'aceest-fitness-gym'
        PYTHON_VER  = '3.12'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Pulling latest code from GitHub...'
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                echo 'Installing Python dependencies...'
                sh '''
                    python3 -m pip install --upgrade pip
                    pip3 install -r requirements.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                echo 'Running flake8 linter...'
                sh '''
                    flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics
                    flake8 app.py --count --max-line-length=120 --statistics --exit-zero
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Running Pytest suite...'
                sh 'pytest tests/ -v --tb=short'
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker image...'
                sh "docker build -t ${APP_NAME}:${BUILD_NUMBER} ."
            }
        }

        stage('Docker Verify') {
            steps {
                echo 'Verifying Docker image...'
                sh "docker images ${APP_NAME}:${BUILD_NUMBER}"
                sh "docker run --rm ${APP_NAME}:${BUILD_NUMBER} python -m pytest tests/ -v --tb=short"
            }
        }
    }

    post {
        success {
            echo "BUILD SUCCESS: ${APP_NAME} build #${BUILD_NUMBER} passed all stages."
        }
        failure {
            echo "BUILD FAILED: ${APP_NAME} build #${BUILD_NUMBER} encountered errors."
        }
        always {
            echo 'Pipeline execution complete.'
        }
    }
}
