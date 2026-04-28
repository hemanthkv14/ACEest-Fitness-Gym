pipeline {
    agent any

    triggers {
        pollSCM('H/2 * * * *')
    }

    environment {
        APP_NAME       = 'aceest-fitness-gym'
        DOCKERHUB_USER = 'hemanth59'
        IMAGE          = "${DOCKERHUB_USER}/${APP_NAME}"
        IMAGE_TAG      = "${IMAGE}:${BUILD_NUMBER}"
        IMAGE_LATEST   = "${IMAGE}:latest"
        TAR_NAME       = "${APP_NAME}-build-${BUILD_NUMBER}.tar"
        K8S_NAMESPACE  = 'aceest'
        SCANNER_HOME   = tool 'SonarQubeScanner'
        // Toggle SonarQube analysis + quality gate. Set to 'true' to enable.
        RUN_SONAR      = 'false'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Pulling latest code from GitHub...'
                checkout scm
            }
        }

        stage('Lint') {
            steps {
                echo 'Running flake8 linter inside python:3.12-slim container...'
                sh '''
                    docker run --rm -v "$WORKSPACE":/app -w /app python:3.12-slim sh -c "
                        pip install --quiet flake8 &&
                        flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics &&
                        flake8 app.py --count --max-line-length=120 --statistics --exit-zero
                    "
                '''
            }
        }

        stage('Test + Coverage') {
            steps {
                echo 'Running pytest with coverage for SonarQube inside python:3.12-slim container...'
                sh '''
                    docker run --rm -v "$WORKSPACE":/app -w /app python:3.12-slim sh -c "
                        pip install --quiet -r requirements.txt &&
                        pytest tests/ -v --tb=short \
                            --cov=app --cov-report=xml:coverage.xml \
                            --junitxml=test-results.xml
                    "
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                    archiveArtifacts artifacts: 'coverage.xml,test-results.xml',
                                     allowEmptyArchive: true
                }
            }
        }

        stage('SonarQube Analysis') {
            when { expression { return env.RUN_SONAR == 'true' } }
            steps {
                echo 'Running SonarQube code analysis...'
                withSonarQubeEnv('SonarQube') {
                    sh """
                        ${SCANNER_HOME}/bin/sonar-scanner \
                          -Dsonar.projectKey=${APP_NAME} \
                          -Dsonar.projectName='ACEest Fitness & Gym' \
                          -Dsonar.sources=app.py \
                          -Dsonar.tests=tests \
                          -Dsonar.test.inclusions=tests/test_app.py \
                          -Dsonar.language=python \
                          -Dsonar.python.version=3.12 \
                          -Dsonar.python.coverage.reportPaths=coverage.xml \
                          -Dsonar.python.xunit.reportPath=test-results.xml
                    """
                }
            }
        }

        stage('Quality Gate') {
            when { expression { return env.RUN_SONAR == 'true' } }
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: false
                }
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker image...'
                sh "docker build -t ${IMAGE_TAG} -t ${IMAGE_LATEST} -t ${IMAGE}:v${BUILD_NUMBER} ."
            }
        }

        stage('Container Smoke Test') {
            steps {
                echo 'Running Pytest inside the built container...'
                sh "docker run --rm ${IMAGE_TAG} python -m pytest tests/ -v --tb=short"
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing image tags to Docker Hub...'
                withCredentials([usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_PASS')]) {
                    sh '''
                        echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                        docker push ${IMAGE_TAG}
                        docker push ${IMAGE_LATEST}
                        docker push ${IMAGE}:v${BUILD_NUMBER}
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes (Rolling Update)') {
            steps {
                echo 'Applying manifests and rolling out new image...'
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    sh '''
                        # Render DOCKERHUB_USER placeholder into manifests
                        find k8s -type f -name '*.yaml' -exec \
                            sed -i "s|DOCKERHUB_USER|${DOCKERHUB_USER}|g" {} +

                        kubectl apply -f k8s/base/namespace.yaml
                        kubectl apply -f k8s/base/service.yaml
                        kubectl apply -f k8s/rolling-update/deployment.yaml

                        kubectl -n ${K8S_NAMESPACE} set image \
                            deployment/aceest-rolling aceest=${IMAGE_TAG}
                        kubectl -n ${K8S_NAMESPACE} rollout status \
                            deployment/aceest-rolling --timeout=180s
                    '''
                }
            }
            post {
                failure {
                    echo 'Deployment failed -- rolling back to previous revision.'
                    withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                        sh '''
                            kubectl -n ${K8S_NAMESPACE} rollout undo \
                                deployment/aceest-rolling || true
                        '''
                    }
                }
            }
        }

        stage('Export Image Artifact') {
            steps {
                sh "docker save ${IMAGE_TAG} ${IMAGE_LATEST} -o ${TAR_NAME}"
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
            sh "rm -f ${TAR_NAME} || true"
            echo 'Pipeline execution complete.'
        }
    }
}
