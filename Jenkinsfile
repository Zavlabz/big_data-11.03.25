pipeline {
  agent any

  environment {
    DB_HOST = 'forum-db'     // имя вашего Postgres‑сервиса из docker-compose
    DB_NAME = 'forum_logs'
    START   = '2023-01-01'
    END     = '2023-01-31'
  }

  stages {
    stage('Extract') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'etl-db',
          usernameVariable: 'DB_USER',
          passwordVariable: 'DB_PSWD'
        )]) {
          sh '''
            echo "Extracting logs to logs_raw.csv..."
            PGPASSWORD=$DB_PSWD psql \
              -h $DB_HOST -U $DB_USER -d $DB_NAME \
              -c "COPY logs TO STDOUT WITH CSV HEADER" \
            > logs_raw.csv
          '''
        }
      }
    }

    stage('Transform & Load') {
      // Весь этот stage будет выполняться в контейнере python:3.9-slim
      agent {
        docker {
          image 'python:3.9-slim'
          // Подключаем к той же сети, что и форум‑БД
          args  '--network pythonproject6_default'
        }
      }
      steps {
        sh '''
          echo "Installing Python dependencies..."
          pip install psycopg2-binary python-dateutil
          echo "Running aggregation script..."
          python aggregate.py "$START" "$END" report.csv
        '''
      }
      post {
        success {
          archiveArtifacts artifacts: 'report.csv', fingerprint: true
        }
      }
    }
  }
}
