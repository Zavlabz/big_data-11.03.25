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
      steps {
        sh '''
          echo "Creating and activating virtualenv..."
          python -m venv venv
          . venv/bin/activate

          echo "Upgrading pip and installing dependencies..."
          pip install --upgrade pip
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
