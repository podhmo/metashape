from __future__ import annotations
import typing as t # noqa F401
from metashape.declarative import (
    field
)
from decimal import (
    Decimal
)
from datetime import (
    datetime
)


class Category:
    __metadata__ = {'tablename': 'Category'}

    id: int = field(default=None, metadata={'primary_key': True})
    name: str


class Customer:
    __metadata__ = {'tablename': 'Customer'}

    id: int = field(default=None, metadata={'primary_key': True})
    email: str
    password: str
    name: str
    country: str
    address: str


class Product:
    __metadata__ = {'tablename': 'Product'}

    id: int = field(default=None, metadata={'primary_key': True})
    name: str
    description: str
    picture: t.Optional[bytes]
    price: Decimal
    quantity: int


class CartItem:
    __metadata__ = {'tablename': 'CartItem'}

    id: int = field(default=None, metadata={'primary_key': True})
    quantity: int
    customer_id: int
    product_id: int


class Category_Product:
    __metadata__ = {'tablename': 'Category_Product'}

    category_id: int = field(default=None, metadata={'primary_key': True})
    product_id: int = field(default=None, metadata={'primary_key': True})


class Order:
    __metadata__ = {'tablename': 'Order'}

    id: int = field(default=None, metadata={'primary_key': True})
    state: str
    date_created: datetime
    date_shipped: t.Optional[datetime]
    date_delivered: t.Optional[datetime]
    total_price: Decimal
    customer_id: int


class OrderItem:
    __metadata__ = {'tablename': 'OrderItem'}

    quantity: int
    price: Decimal
    order_id: int = field(default=None, metadata={'primary_key': True})
    product_id: int = field(default=None, metadata={'primary_key': True})
