import os
import time

# Папка с логами
directory = 'logs'

def purge_old_logs():
    now = time.time()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and (now - os.path.getmtime(file_path)) > 3600:
            os.remove(file_path)
            print(f"🗑️ Удалён файл: {file_path}")

if __name__ == "__main__":
    while True:
        purge_old_logs()
        time.sleep(3600)  # 1 раз в час
