pipeline {
  agent any

  environment {
    DB_HOST     = 'forum-db'
    DB_NAME     = 'forum_logs'
    DB_USER     = 'admin'
    DB_PASSWORD = 'secret'
    DB_PORT     = '5432'
    START       = '2023-01-01'
    END         = '2023-01-31'
  }

  stages {
    stage('Extract') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'etl-db',
          usernameVariable: 'CRED_USER',
          passwordVariable: 'CRED_PSWD'
        )]) {
          sh '''
            echo "Extracting logs to logs_raw.csv..."
            PGPASSWORD=$CRED_PSWD psql \
              -h $DB_HOST -U $CRED_USER -d $DB_NAME \
              -c "COPY logs TO STDOUT WITH CSV HEADER" \
            > logs_raw.csv
          '''
        }
      }
    }

    stage('Transform & Load') {
      steps {
        sh '''
          echo "Creating virtualenv and installing deps..."
          python -m venv venv
          . venv/bin/activate
          pip install --upgrade pip
          pip install psycopg2-binary python-dateutil

          echo "Running aggregation..."
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
