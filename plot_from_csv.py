import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_from_csv(csv_file='container_stats.csv'):
    # Загружаем данные из CSV файла
    df = pd.read_csv(csv_file, parse_dates=['Timestamp'])

    # Группируем данные по контейнерам
    containers = df['Container Name'].unique()

    # Создаем фигуру с несколькими графиками
    fig, axs = plt.subplots(3, 1, figsize=(19.2, 12), sharex=True)

    for container in containers:
        container_data = df[df['Container Name'] == container]

        # График CPU
        axs[0].plot(container_data['Timestamp'], container_data['CPU (%)'], label=f'{container} CPU (%)')
        axs[0].set_ylabel('CPU (%)')
        axs[0].set_title('CPU Usage Over Time')
        axs[0].grid(True)

        # График памяти
        axs[1].plot(container_data['Timestamp'], container_data['Memory Usage (MB)'], label=f'{container} Memory (MB)')
        axs[1].set_ylabel('Memory (MB)')
        axs[1].set_title('Memory Usage Over Time')
        axs[1].grid(True)

        # График сетевой активности
        axs[2].plot(container_data['Timestamp'], container_data['Network RX (MB)'],
                    label=f'{container} Network RX (MB)', linestyle='--')
        axs[2].plot(container_data['Timestamp'], container_data['Network TX (MB)'],
                    label=f'{container} Network TX (MB)', linestyle='--')
        axs[2].set_ylabel('Network (MB)')
        axs[2].set_title('Network I/O Over Time')
        axs[2].grid(True)

    # Настройки оси X (время)
    axs[2].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate()  # Автоматический поворот меток времени

    # Настройка легенд: Размещение под графиком с несколькими строками и уменьшенным шрифтом
    for ax in axs:
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.3), ncol=4, fontsize='x-small', frameon=False)

    # Применяем tight_layout для оптимальной компоновки
    plt.tight_layout()

    # Увеличиваем нижнее поле для размещения легенды
    plt.subplots_adjust(bottom=0.3)

    # Показываем график
    plt.show()

if __name__ == "__main__":
    # Вызываем функцию для построения графика
    plot_from_csv('container_stats.csv')
