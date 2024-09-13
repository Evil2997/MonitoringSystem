import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import base64
from io import BytesIO


# Функция для сортировки контейнеров по группам
def group_containers(df):
    venom_group = df[df['Container Name'].str.startswith('venom')]
    natrix_group = df[df['Container Name'].str.startswith('natrix')]
    audit_group = df[df['Container Name'].str.startswith('audit')]
    other_group = df[~df['Container Name'].str.startswith(('venom', 'natrix', 'audit'))]

    return venom_group, natrix_group, audit_group, other_group


# Функция для создания графиков по группам
def create_plot(group, group_name):
    fig, axs = plt.subplots(3, 1, figsize=(14, 14), sharex=True)

    containers = group['Container Name'].unique()

    for container in containers:
        container_data = group[group['Container Name'] == container]

        # График CPU
        axs[0].plot(container_data['Timestamp'], container_data['CPU (%)'], label=f'{container} CPU (%)')
        axs[0].set_ylabel('CPU (%)')
        axs[0].set_title(f'{group_name} CPU Usage Over Time')
        axs[0].grid(True)
        axs[0].set_ylim(0, 100)  # Лимит для оси Y от 0 до 100%

        # График памяти
        axs[1].plot(container_data['Timestamp'], container_data['Memory Usage (MB)'], label=f'{container} Memory (MB)')
        axs[1].set_ylabel('Memory (MB)')
        axs[1].set_title(f'{group_name} Memory Usage Over Time')
        axs[1].grid(True)

        # График сетевой активности
        axs[2].plot(container_data['Timestamp'], container_data['Network RX (MB)'],
                    label=f'{container} Network RX (MB)', linestyle='--')
        axs[2].plot(container_data['Timestamp'], container_data['Network TX (MB)'],
                    label=f'{container} Network TX (MB)', linestyle='--')
        axs[2].set_ylabel('Network (MB)')
        axs[2].set_title(f'{group_name} Network I/O Over Time')
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

    # Закрываем буфер и график
    buffer.close()
    plt.close(fig)

    return image_base64


# Функция для генерации HTML
def generate_html(venom_img, natrix_img, audit_img, other_img):
    html = f"""
    <html>
    <head><title>Container Monitoring Graphs</title></head>
    <body>
    <h1>Monitoring Results</h1>

    <h2>Venom Group</h2>
    <img src="data:image/png;base64,{venom_img}" alt="Venom Group Graphs">

    <h2>Natrix Group</h2>
    <img src="data:image/png;base64,{natrix_img}" alt="Natrix Group Graphs">

    <h2>Audit Group</h2>
    <img src="data:image/png;base64,{audit_img}" alt="Audit Group Graphs">

    <h2>Other Group</h2>
    <img src="data:image/png;base64,{other_img}" alt="Other Group Graphs">

    </body>
    </html>
    """

    with open('monitoring_graph.html', 'w') as f:
        f.write(html)

    print("HTML файл сохранен как 'monitoring_graph.html'")


# Главная функция
def plot_from_csv(csv_file='container_stats.csv'):
    # Загружаем данные из CSV файла
    df = pd.read_csv(csv_file, parse_dates=['Timestamp'])

    # Сортируем контейнеры по группам
    venom_group, natrix_group, audit_group, other_group = group_containers(df)

    # Создаем графики для каждой группы
    venom_img = create_plot(venom_group, 'Venom Group')
    natrix_img = create_plot(natrix_group, 'Natrix Group')
    audit_img = create_plot(audit_group, 'Audit Group')
    other_img = create_plot(other_group, 'Other Group')

    # Генерируем HTML
    generate_html(venom_img, natrix_img, audit_img, other_img)


if __name__ == "__main__":
    # Вызываем функцию для построения графиков и генерации HTML
    plot_from_csv('container_stats.csv')
