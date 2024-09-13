import docker
import time
import json
import logging
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Храним предыдущие данные для каждого контейнера и историю для графиков
previous_stats = {}
data_history = defaultdict(lambda: defaultdict(list))  # Храним историю по каждому контейнеру и параметру


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
        'status': container.status
    }


def monitor_container(container):
    return get_container_stats(container)


def compare_stats(new_stats, old_stats):
    """Сравнивает старые и новые данные контейнера, возвращает True, если они отличаются"""
    return new_stats != old_stats


def update_data_history(stats):
    """Записывает новые данные в историю для дальнейшего построения графиков"""
    container_name = stats['name']
    timestamp = time.time()  # Текущее время для графиков

    data_history[container_name]['time'].append(timestamp)
    data_history[container_name]['cpu_percentage'].append(stats['cpu_percentage'])
    data_history[container_name]['memory_usage_mb'].append(stats['memory_usage_mb'])
    data_history[container_name]['memory_percentage'].append(stats['memory_percentage'])
    data_history[container_name]['network_rx_mb'].append(stats['network_rx_mb'])
    data_history[container_name]['network_tx_mb'].append(stats['network_tx_mb'])


def plot_graphs():
    """Строит графики на основе данных"""
    plt.clf()  # Очищаем график перед рисованием

    for container_name, data in data_history.items():
        times = data['time']

        # Строим графики для каждого параметра
        plt.subplot(3, 1, 1)
        plt.plot(times, data['cpu_percentage'], label=f'{container_name} CPU (%)')
        plt.ylabel('CPU %')

        plt.subplot(3, 1, 2)
        plt.plot(times, data['memory_usage_mb'], label=f'{container_name} Memory (MB)')
        plt.ylabel('Memory (MB)')

        plt.subplot(3, 1, 3)
        plt.plot(times, data['network_rx_mb'], label=f'{container_name} Network RX (MB)')
        plt.plot(times, data['network_tx_mb'], label=f'{container_name} Network TX (MB)')
        plt.ylabel('Network (MB)')

    plt.xlabel('Time (s)')
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.pause(0.1)  # Обновляем графики


def monitor_containers():
    client = docker.from_env()

    plt.ion()  # Включаем интерактивный режим графиков
    plt.figure(figsize=(10, 8))

    try:
        while True:
            containers = client.containers.list()
            data = []

            # Используем ThreadPoolExecutor для многопоточности
            with ThreadPoolExecutor() as executor:
                results = executor.map(monitor_container, containers)

            for stats in results:
                container_name = stats['name']

                # Проверяем, изменились ли данные с прошлого раза
                if container_name not in previous_stats or compare_stats(stats, previous_stats[container_name]):
                    # Обновляем предыдущие данные
                    previous_stats[container_name] = stats
                    update_data_history(stats)  # Обновляем историю данных для графиков

            plot_graphs()  # Обновляем графики
            time.sleep(10)
    except KeyboardInterrupt:
        logging.info("Мониторинг остановлен.")
        plt.ioff()
        plt.show()  # Показываем графики перед завершением программы


if __name__ == "__main__":
    monitor_containers()
