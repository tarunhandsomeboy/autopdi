
pipeline {
    agent any

    options {
        timestamps()
    }

    environment {
        IMAGE_NAME = 'autopdi-app'
        IMAGE_TAG = '1.0'

        CONTAINER_NAME = 'autopdi-jenkins-test'
        HOST_PORT = '5001'
        APP_PORT = '5000'

        DOCKER_EXE = 'C:\\Users\\Varun\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'AUTO PDI source code is ready.'
                echo 'Using the Jenkins workspace.'
            }
        }

        stage('Check Docker') {
            steps {
                bat '"%DOCKER_EXE%" --version'
                bat '"%DOCKER_EXE%" info'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '"%DOCKER_EXE%" build -t %IMAGE_NAME%:%IMAGE_TAG% .'
            }
        }

        stage('Verify Docker Image') {
            steps {
                bat '"%DOCKER_EXE%" image inspect %IMAGE_NAME%:%IMAGE_TAG%'
            }
        }

        stage('Deploy AUTO PDI Test') {
            steps {
                script {
                    echo 'Removing previous AUTO PDI test container, if present.'

                    bat(
                        returnStatus: true,
                        script: '"%DOCKER_EXE%" rm -f %CONTAINER_NAME%'
                    )

                    echo 'Starting new AUTO PDI test container.'

                    bat '"%DOCKER_EXE%" run -d --name %CONTAINER_NAME% -p %HOST_PORT%:%APP_PORT% %IMAGE_NAME%:%IMAGE_TAG%'

                    echo 'Waiting for the application to start.'
                    sleep(time: 10, unit: 'SECONDS')

                    echo 'Checking AUTO PDI website response.'

                    bat 'curl.exe --fail --silent --show-error --location --max-time 30 http://localhost:5001/ -o NUL'
                }
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: AUTO PDI image built, deployed and verified.'
            echo 'Test website: http://localhost:5001'
        }

        failure {
            echo 'FAILED: Check Console Output for the first error.'
        }

        always {
            echo 'AUTO PDI Jenkins pipeline finished.'
        }
    }
}
