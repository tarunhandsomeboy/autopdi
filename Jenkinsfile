
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'AUTO PDI source code is ready'
            }
        }

        stage('Check Docker') {
            steps {
                bat 'docker --version'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t autopdi-app:1.0 .'
            }
        }

        stage('Verify Docker Image') {
            steps {
                bat 'docker image inspect autopdi-app:1.0'
            }
        }
    }

    post {
        success {
            echo 'AUTO PDI Docker build completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check Console Output.'
        }
    }
}
