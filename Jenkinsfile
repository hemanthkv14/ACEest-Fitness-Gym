pipeline {
    agent any

    triggers {
        pollSCM('H/2 * * * *')
    }

    environment {
        APP_NAME    = 'aceest-fitness-gym'
        IMAGE_TAG   = "${APP_NAME}:${BUILD_NUMBER}"
        TAR_NAME    = "aceest-fitness-gym-build-${BUILD_NUMBER}.tar"
        SCANNER_HOME = tool 'SonarQubeScanner'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Pulling latest code from GitHub...'
                checkout scm
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo 'Running SonarQube code analysis...'
                withSonarQubeEnv('SonarQube') {
                    sh """
                        ${SCANNER_HOME}/bin/sonar-scanner \
                        -Dsonar.projectKey=${APP_NAME} \
                        -Dsonar.projectName='ACEest Fitness & Gym' \
                        -Dsonar.sources=. \
                        -Dsonar.inclusions=app.py \
                        -Dsonar.tests=tests \
                        -Dsonar.test.inclusions=tests/test_app.py \
                        -Dsonar.language=python \
                        -Dsonar.python.version=3.12 \
                        -Dsonar.login=\${SONAR_AUTH_TOKEN}
                    """
                }
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker image...'
                sh "docker build -t ${IMAGE_TAG} ."
                sh "docker tag ${IMAGE_TAG} ${APP_NAME}:latest"
            }
        }

        stage('Lint') {
            steps {
                echo 'Running flake8 linter inside container...'
                sh "docker run --rm ${IMAGE_TAG} flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics"
                sh "docker run --rm ${IMAGE_TAG} flake8 app.py --count --max-line-length=120 --statistics --exit-zero"
            }
        }

        stage('Test') {
            steps {
                echo 'Running Pytest suite inside container...'
                sh "docker run --rm ${IMAGE_TAG} python -m pytest tests/ -v --tb=short"
            }
        }

        stage('Export Docker Image') {
            steps {
                echo 'Saving Docker image as downloadable artifact...'
                sh "docker save ${IMAGE_TAG} ${APP_NAME}:latest -o ${TAR_NAME}"
                archiveArtifacts artifacts: "${TAR_NAME}", fingerprint: true
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
            sh "rm -f ${TAR_NAME} || true"
        }
    }
}
