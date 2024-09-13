import csv
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import docker


def get_container_stats(container):
    stats = container.stats(stream=False)

    cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
    system_cpu_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
    num_cpus = len(stats['cpu_stats']['cpu_usage'].get('percpu_usage', [1]))
    cpu_percentage = (cpu_delta / system_cpu_delta) * num_cpus * 100 if system_cpu_delta > 0 else 0.0

    memory_usage = stats['memory_stats']['usage']
    memory_limit = stats['memory_stats']['limit']
    memory_percentage = (memory_usage / memory_limit) * 100

    network_rx_bytes = stats['networks']['eth0']['rx_bytes'] if 'networks' in stats and 'eth0' in stats[
        'networks'] else 0
    network_tx_bytes = stats['networks']['eth0']['tx_bytes'] if 'networks' in stats and 'eth0' in stats[
        'networks'] else 0

    return {
        'name': container.name,
        'cpu_percentage': cpu_percentage,
        'memory_usage_mb': memory_usage / 1024 / 1024,
        'memory_limit_mb': memory_limit / 1024 / 1024,
        'memory_percentage': memory_percentage,
        'network_rx_mb': network_rx_bytes / 1024 / 1024,
        'network_tx_mb': network_tx_bytes / 1024 / 1024,
        'status': container.status,
        'timestamp': datetime.now()
    }


def monitor_container(container):
    return get_container_stats(container)


def save_stats_to_csv(stats, csv_writer):
    """Записываем данные в CSV файл"""
    csv_writer.writerow([
        stats['timestamp'],
        stats['name'],
        stats['cpu_percentage'],
        stats['memory_usage_mb'],
        stats['memory_percentage'],
        stats['network_rx_mb'],
        stats['network_tx_mb'],
        stats['status']
    ])


def monitor_containers(output_file='container_stats.csv'):
    client = docker.from_env()

    # Открываем CSV файл и пишем заголовки
    with open(output_file, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        # Пишем заголовки
        csv_writer.writerow([
            'Timestamp', 'Container Name', 'CPU (%)', 'Memory Usage (MB)', 'Memory Usage (%)',
            'Network RX (MB)', 'Network TX (MB)', 'Status'
        ])

        try:
            while True:
                containers = client.containers.list()

                with ThreadPoolExecutor() as executor:
                    results = executor.map(monitor_container, containers)

                for stats in results:
                    save_stats_to_csv(stats, csv_writer)  # Записываем данные в CSV

                time.sleep(25)  # Пауза между обновлениями
        except KeyboardInterrupt:
            logging.info("Мониторинг остановлен. Запись в CSV завершена.")
        except Exception as e:
            logging.error(f"Ошибка: {e}")
        finally:
            logging.info("Файл CSV закрыт.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Запускаем мониторинг контейнеров с записью данных в CSV
    monitor_containers(output_file="container_stats.csv")
