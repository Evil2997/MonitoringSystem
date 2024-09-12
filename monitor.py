import docker
import time
import json
import logging
from concurrent.futures import ThreadPoolExecutor

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Храним предыдущие данные для каждого контейнера
previous_stats = {}
OUTPUT_JSON = "containers_stats.json"

def get_container_stats(container):
    try:
        # Получаем статистику контейнера
        stats = container.stats(stream=False)

        # Получаем данные по использованию CPU
        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
        system_cpu_delta = stats['cpu_stats'].get('system_cpu_usage', 0) - stats['precpu_stats'].get('system_cpu_usage', 0)
        num_cpus = len(stats['cpu_stats']['cpu_usage'].get('percpu_usage', [1]))
        cpu_percentage = round((cpu_delta / system_cpu_delta) * num_cpus * 100, 2) if system_cpu_delta > 0 else 0.0

        # Получаем данные по использованию памяти
        memory_usage = stats['memory_stats']['usage']
        memory_limit = stats['memory_stats']['limit']
        memory_percentage = round((memory_usage / memory_limit) * 100, 2)

        # Получаем данные по сетевому I/O
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

def monitor_container(container):
    return get_container_stats(container)

def compare_stats(new_stats, old_stats):
    """Сравнивает старые и новые данные контейнера, возвращает True, если они отличаются"""
    return new_stats != old_stats

def write_to_json(data):
    """Запись всех данных в один JSON-файл с отступом 2"""
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(data, f, indent=2)

def monitor_containers():
    client = docker.from_env()

    try:
        while True:
            # Получаем все контейнеры (включая остановленные)
            containers = client.containers.list(all=True)

            # Используем ThreadPoolExecutor для многопоточности
            with ThreadPoolExecutor() as executor:
                results = executor.map(monitor_container, containers)

            # Сохраняем и выводим данные в один JSON
            for stats in results:
                if stats:
                    container_name = stats['name']

                    # Проверяем, изменились ли данные с прошлого раза
                    if container_name not in previous_stats or compare_stats(stats, previous_stats[container_name]):
                        # Обновляем предыдущие данные
                        previous_stats[container_name] = stats

            # Записываем все данные в один JSON-файл
            write_to_json(list(previous_stats.values()))

            logging.info(f"Данные по контейнерам обновлены. Сохранено {len(previous_stats)} контейнеров.")

            time.sleep(5)
    except KeyboardInterrupt:
        logging.info("Мониторинг остановлен.")
    except Exception as e:
        logging.error(f"Ошибка при мониторинге: {e}")

if __name__ == "__main__":
    monitor_containers()
