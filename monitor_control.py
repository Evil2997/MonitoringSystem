import subprocess
import time
import json
import os

CONTAINER_NAME = "docker-monitor"

def start_monitoring_container():
    """Запуск Docker-контейнера для мониторинга"""
    print("Запуск контейнера для мониторинга...")
    subprocess.run([
        "docker", "run", "--name", CONTAINER_NAME, "--rm", "-d",
        "-v", "/var/run/docker.sock:/var/run/docker.sock",
        "-v", f"{os.getcwd()}:/app",  # Монтируем текущую директорию для получения JSON-файлов
        "docker-monitor"
    ], check=True)

def read_json_files():
    """Чтение JSON-файлов, созданных контейнером мониторинга"""
    while True:
        for file in os.listdir("."):
            if file.endswith("_stats.json"):
                with open(file, "r") as f:
                    data = json.load(f)
                    print(f"Результаты из {file}:")
                    print(json.dumps(data, indent=2))

        time.sleep(2)

if __name__ == "__main__":
    try:
        start_monitoring_container()
        read_json_files()
    except KeyboardInterrupt:
        print("Остановка мониторинга...")
        subprocess.run(["docker", "stop", CONTAINER_NAME])



