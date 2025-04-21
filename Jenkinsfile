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
    // Делаем всё через один shell‑скрипт
    sh '''
      # 1. Создаём виртуальное окружение
      python3 -m venv venv
      # 2. Активируем его
      . venv/bin/activate
      # 3. Обновляем pip и ставим зависимости внутрь venv
      pip install --upgrade pip
      pip install psycopg2-binary python-dateutil
      # 4. Запускаем ваш агрегатор
      python aggregate.py "$START" "$END" report.csv
    '''
  }
  post {
    success {
      archiveArtifacts artifacts: 'report.csv', fingerprint: true
    }
  }
}

