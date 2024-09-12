import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor

import docker

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

previous_stats = {}
OUTPUT_JSON = "system_containers_stats.json"


def get_container_stats(container):
    """Получение статистики Docker-контейнера"""
    try:
        stats = container.stats(stream=False)

        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
        system_cpu_delta = stats['cpu_stats'].get('system_cpu_usage', 0) - stats['precpu_stats'].get('system_cpu_usage',
                                                                                                     0)
        num_cpus = len(stats['cpu_stats']['cpu_usage'].get('percpu_usage', [1]))
        cpu_percentage = round((cpu_delta / system_cpu_delta) * num_cpus * 100, 2) if system_cpu_delta > 0 else 0.0

        memory_stats = stats.get('memory_stats', {})
        memory_usage = memory_stats.get('usage', 0)
        memory_limit = memory_stats.get('limit', 1)  # Избегаем деления на 0
        memory_percentage = round((memory_usage / memory_limit) * 100, 2)

        network_stats = stats.get('networks', {})
        network_rx_bytes = sum(interface.get('rx_bytes', 0) for interface in network_stats.values())
        network_tx_bytes = sum(interface.get('tx_bytes', 0) for interface in network_stats.values())

        return {
            'name': container.name,
            'cpu_percentage': cpu_percentage,
            'memory_usage_mb': round(memory_usage / 1024 / 1024, 2),
            'memory_limit_mb': round(memory_limit / 1024 / 1024, 2),
            'memory_percentage': memory_percentage,
            'network_rx_mb': round(network_rx_bytes / 1024 / 1024, 2),
            'network_tx_mb': round(network_tx_bytes / 1024 / 1024, 2),
            'status': container.status
        }
    except Exception as e:
        logging.error(f"Ошибка получения статистики для контейнера {container.name}: {e}")
        return None


def write_to_json(data):
    """Запись всех данных в один JSON-файл с отступом 2"""
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(data, f, indent=2)


def monitor_all():
    client = docker.from_env()

    try:
        while True:
            containers = client.containers.list(all=True)  # Получаем все контейнеры
            data = {}

            # Собираем статистику контейнеров
            with ThreadPoolExecutor() as executor:
                container_results = list(executor.map(get_container_stats, containers))
                data['containers'] = [result for result in container_results if result]

            write_to_json(data)

            logging.info(f"Данные обновлены и сохранены в {OUTPUT_JSON}.")
            time.sleep(5)
    except KeyboardInterrupt:
        logging.info("Мониторинг остановлен.")
    except Exception as e:
        logging.error(f"Ошибка при мониторинге: {e}")


if __name__ == "__main__":
    monitor_all()
