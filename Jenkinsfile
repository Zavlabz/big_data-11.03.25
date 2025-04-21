pipeline {
  agent any

  environment {
    // Имя контейнера БД из Docker‑Compose
    DB_HOST = 'forum-db'
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
            # выдираем логи в CSV
            PGPASSWORD=$DB_PSWD psql \
              -h $DB_HOST -U $DB_USER -d $DB_NAME \
              -c "COPY logs TO STDOUT WITH CSV HEADER" \
            > logs_raw.csv
          '''
        }
      }
    }

    stage('Transform & Load') {
      agent {
        docker {
          image 'python:3.9-slim'
          // Убедитесь, что сеть совпадает с вашим docker-compose
          args  '--network pythonproject6_default'
        }
      }
      steps {
        sh '''
          # устанавливаем зависимости и запускаем агрегатор
          pip install psycopg2-binary python-dateutil
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
