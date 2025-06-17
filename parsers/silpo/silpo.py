import aiohttp
from bs4 import BeautifulSoup


async def parse_atb_promotions():
    url = "https://silpo.ua/category/spetsialni-propozytsii-5189"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()

    soup = BeautifulSoup(html, 'lxml')
    promotions = []

    # Тут логіка парсингу конкретних елементів
    for item in soup.select('.promotion-item'):
        name = item.select_one('.promo-title').text.strip()
        price = item.select_one('.promo-price').text.strip()
        promotions.append({'name': name, 'price': price, 'store': 'ATB'})

    return promotions