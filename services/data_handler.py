import pandas as pd
from datetime import datetime


async def save_to_csv(data, filename='prices.csv'):
    df = pd.DataFrame(data)

    # Додаємо timestamp
    df['timestamp'] = datetime.now()

    # Зберігаємо у CSV (додаємо нові дані, не перезаписуємо файл)
    try:
        existing = pd.read_csv(filename)
        updated = pd.concat([existing, df])
        updated.to_csv(filename, index=False)
    except FileNotFoundError:
        df.to_csv(filename, index=False)