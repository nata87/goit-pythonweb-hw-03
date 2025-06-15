# Вибираємо офіційний Python образ
FROM python:3.10

# Встановлюємо Jinja2
RUN pip install jinja2

# Копіюємо всі файли у контейнер
WORKDIR /app
COPY . .

# Відкриваємо порт 3000
EXPOSE 3000

# Запускаємо наш Python скрипт
CMD ["python", "main.py"]
