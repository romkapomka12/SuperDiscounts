from dataclasses import dataclass, fields


@dataclass
class ProductDetail:
    title: str
    price: float
    old_price: float
    date: str


PRODUCT_FIELDS = [field.name for field  in fields (ProductDetail)]