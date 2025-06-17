from dataclasses import dataclass, fields


@dataclass
class ProductDetail:
    title: str
    price: float


PRODUCT_FIELDS = [field.name for field  in fields (ProductDetail)]