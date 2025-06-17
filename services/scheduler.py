from celery import Celery
from parsers import atb, novus, silpo
from services.data_handler import save_to_csv

app = Celery('price_tracker', broker='redis://localhost:6379/0')


@app.task
async def run_parsers():
    results = []
    for parser in [
        atb.parse_atb_promotions,
        novus.parse_novus_promotions,
        silpo.parse_silpo_promotions
    ]:

        data = await parser()
        results.extend(data)

    await save_to_csv(results)