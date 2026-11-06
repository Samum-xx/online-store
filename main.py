"""Ядро e-commerce: сущности «Продукт» и «Категория» + загрузка JSON."""
import json
from typing import Any, Dict, List, Optional


class Product:
    """Товар магазина: название, описание, цена, количество на складе."""

    def __init__(
        self,
        name: str,
        description: str,
        price: float,
        quantity: int,
    ) -> None:
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity


class Category:
    """Категория товаров.

    Атрибуты класса category_count и product_count хранят общую
    статистику по всем созданным категориям и обновляются
    автоматически при создании нового объекта.
    """

    category_count: int = 0
    product_count: int = 0

    def __init__(
        self,
        name: str,
        description: str,
        products: Optional[List[Product]] = None,
    ) -> None:
        self.name = name
        self.description = description
        self.products: List[Product] = (
            products if products is not None else []
        )
        Category.category_count += 1
        Category.product_count += len(self.products)


def load_products_from_json(filepath: str) -> List[Category]:
    """Читает JSON-файл и создаёт объекты категорий и товаров."""
    with open(filepath, "r", encoding="utf-8") as file:
        data: List[Dict[str, Any]] = json.load(file)

    categories: List[Category] = []
    for category_data in data:
        products = [
            Product(
                name=item["name"],
                description=item["description"],
                price=item["price"],
                quantity=item["quantity"],
            )
            for item in category_data.get("products", [])
        ]
        categories.append(
            Category(
                name=category_data["name"],
                description=category_data["description"],
                products=products,
            )
        )
    return categories


if __name__ == "__main__":
    product1 = Product(
        "Samsung Galaxy S23 Ultra",
        "256GB, Серый цвет, 200MP камера",
        180000.0,
        5,
    )
    product2 = Product("Iphone 15", "512GB, Gray space", 210000.0, 8)
    product3 = Product("Xiaomi Redmi Note 11", "1024GB, Синий", 31000.0, 14)

    print(product1.name)
    print(product1.description)
    print(product1.price)
    print(product1.quantity)

    print(product2.name)
    print(product2.description)
    print(product2.price)
    print(product2.quantity)

    print(product3.name)
    print(product3.description)
    print(product3.price)
    print(product3.quantity)

    description_phones = (
        "Смартфоны, как средство не только коммуникации, "
        "но и получение дополнительных функций для удобства жизни"
    )
    category1 = Category(
        "Смартфоны",
        description_phones,
        [product1, product2, product3],
    )

    print(category1.name == "Смартфоны")
    print(category1.description)
    print(len(category1.products))
    print(category1.category_count)
    print(category1.product_count)

    product4 = Product(
        "55\" QLED 4K",
        "Фоновая подсветка",
        123000.0,
        7,
    )
    description_tvs = (
        "Современный телевизор, который позволяет наслаждаться "
        "просмотром, станет вашим другом и помощником"
    )
    category2 = Category("Телевизоры", description_tvs, [product4])

    print(category2.name)
    print(category2.description)
    print(len(category2.products))
    print(category2.products)

    print(Category.category_count)
    print(Category.product_count)
