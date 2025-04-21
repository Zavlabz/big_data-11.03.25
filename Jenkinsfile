stage('Extract') {
  steps {
    withCredentials([usernamePassword(credentialsId: 'etl-db',
                                     usernameVariable: 'DB_USER',
                                     passwordVariable: 'DB_PSWD')]) {
      sh '''
        PGPASSWORD=$DB_PSWD \
        psql -h forum-db -U $DB_USER -d forum_logs \
          -c "COPY logs TO STDOUT WITH CSV HEADER" \
        > logs_raw.csv
      '''
    }
  }
}

stage('Transform & Load') {
  steps {
    sh '''
      # Создаём виртуальное окружение
      python3 -m venv venv
      # Активируем его
      . venv/bin/activate
      # Устанавливаем зависимости внутрь venv
      pip install --upgrade pip
      pip install psycopg2-binary python-dateutil
      # Запускаем ваш агрегатор
      python aggregate.py "$START" "$END" report.csv
    '''
  }
}

