pipeline {
  agent any

  environment {
    DB_HOST = 'forum-db'
    DB_NAME = 'forum_logs'
    START   = '2023-01-01'
    END     = '2023-01-31'
  }

  stages {
    stage('Extract') {
      agent {
        docker {
          image 'postgres:13'
          args  '--network pythonproject6_default'
        }
      }
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'etl-db',
          usernameVariable: 'DB_USER',
          passwordVariable: 'DB_PSWD'
        )]) {
          sh '''
            echo "Extracting logs..."
            PGPASSWORD=$DB_PSWD psql -h $DB_HOST -U $DB_USER -d $DB_NAME \
              -c "COPY logs TO STDOUT WITH CSV HEADER" > logs_raw.csv
          '''
        }
      }
    }

    stage('Transform & Load') {
      agent {
        docker {
          image 'python:3.9-slim'
          args  '--network pythonproject6_default'
        }
      }
      steps {
        sh '''
          echo "Installing Python deps and running aggregation..."
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
