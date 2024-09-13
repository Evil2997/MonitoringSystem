import base64
from io import BytesIO

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


def plot_from_csv(csv_file='container_stats.csv'):
    # Загружаем данные из CSV файла
    df = pd.read_csv(csv_file, parse_dates=['Timestamp'])

    # Группируем данные по контейнерам
    containers = df['Container Name'].unique()

    # Создаем фигуру с несколькими графиками
    fig, axs = plt.subplots(3, 1, figsize=(14, 14), sharex=True)

    for container in containers:
        container_data = df[df['Container Name'] == container]

        # График CPU
        axs[0].plot(container_data['Timestamp'], container_data['CPU (%)'], label=f'{container} CPU (%)')
        axs[0].set_ylabel('CPU (%)')
        axs[0].set_title('CPU Usage Over Time')
        axs[0].grid(True)

        # Устанавливаем пределы для оси Y от 0 до 100 для графика CPU
        axs[0].set_ylim(0, 100)

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

    # Сохраняем график в буфер
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Конвертируем изображение в base64
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Закрываем буфер
    buffer.close()

    # Генерируем HTML
    html = f"""
    <html>
    <head><title>Container Monitoring Graph</title></head>
    <body>
    <h1>Monitoring Results</h1>
    <img src="data:image/png;base64,{image_base64}" alt="Monitoring Graph">
    </body>
    </html>
    """

    # Записываем HTML в файл
    with open('monitoring_graph.html', 'w') as f:
        f.write(html)

    print("HTML файл сохранен как 'monitoring_graph.html'")


if __name__ == "__main__":
    # Вызываем функцию для построения графика
    plot_from_csv('container_stats.csv')
