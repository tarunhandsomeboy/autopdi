
pipeline {
    agent any

    options {
        timestamps()
    }

    environment {
        DOCKER_EXE = 'C:\\Users\\Varun\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
        IMAGE_NAME = 'autopdi-app'
        IMAGE_TAG = '1.0'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'AUTO PDI source code is ready.'
                bat 'git --version'
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
    }

    post {
        success {
            echo 'SUCCESS: AUTO PDI Docker image built and verified.'
        }

        failure {
            echo 'FAILED: Check Console Output for the first error.'
        }

        always {
            echo 'AUTO PDI Jenkins pipeline finished.'
        }
    }
}
