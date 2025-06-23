from dataclasses import dataclass, fields


@dataclass
class ProductDetail:
    title: str
    price: float
    old_price: float
    date: str
    image_url: str
    tag_shop: str


PRODUCT_FIELDS = [field.name for field  in fields (ProductDetail)]