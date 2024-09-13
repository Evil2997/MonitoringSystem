# Container Monitoring System

Этот проект предназначен для мониторинга Docker-контейнеров и записи их метрик (CPU, память, сеть) в CSV файл.

## Установка

1. Склонируйте репозиторий:
    ```bash
    git clone https://github.com/Evil2997/MonitoringSystem
    cd MonitoringSystem
   ```
2. Установите виртуальное окружение:
   ```bash
    python3 -m venv venv
    source venv/bin/activate
   ```
3. Установите зависимости
   ```bash
   pip install -r requirements.txt
   ```

## Использование:

1. Запустите скрипт мониторинга контейнеров:
    ```bash
    python3 monitor.py
    ```
