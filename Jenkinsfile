// CI/CD: Build → Push (DockerHub) → Deploy (Ansible on EC2)
pipeline {
  agent any

  environment {
    DOCKERHUB_REPO = 'ozposner/myapp'
  }

  options { timestamps() }

  stages {

    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Compute Tag') {
      steps {
        script {
          def shortSha = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
          env.IMAGE_TAG  = "${env.BUILD_NUMBER}-${shortSha}"
          env.IMAGE_NAME = "${env.DOCKERHUB_REPO}:${env.IMAGE_TAG}"
          echo "Using image tag: ${env.IMAGE_TAG}"
        }
      }
    }

    stage('Docker Build') {
      steps {
        sh "docker build -t ${env.IMAGE_NAME} ."
      }
    }

    stage('Push to DockerHub') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                          usernameVariable: 'DOCKER_USER',
                                          passwordVariable: 'DOCKER_PASS')]) {
          sh """
            echo "\$DOCKER_PASS" | docker login -u "\$DOCKER_USER" --password-stdin
            docker push ${env.IMAGE_NAME}
            docker logout
          """
        }
      }
    }

    stage('Deploy with Ansible') {
      steps {
        withCredentials([sshUserPrivateKey(credentialsId: 'ansible-ssh',
                                           keyFileVariable: 'SSH_KEY',
                                           usernameVariable: 'SSH_USER')]) {
          sh """
            cd ansible
            ansible-galaxy collection install community.docker

            echo "Deploying tag: ${env.IMAGE_TAG} to repo: ${env.DOCKERHUB_REPO}"
            ansible-playbook -i inventory.ini deploy-playbook.yml \\
              --private-key "$SSH_KEY" -u "$SSH_USER" \\
              -e "image_repo=${env.DOCKERHUB_REPO}" \\
              -e "image_tag=${env.IMAGE_TAG}" \\
              -e "app_name=myapp" \\
              -e "host_port=80" \\
              -e "container_port=5000"
          """
        }
      }
    }
  }

  post {
    always {
      sh 'docker images | head -n 10 || true'
    }
  }
}

