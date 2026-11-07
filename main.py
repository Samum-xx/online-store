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
        self.__price = price
        self.quantity = quantity

    @property
    def price(self) -> float:
        """Возвращает текущую цену товара."""
        return self.__price

    @price.setter
    def price(self, new_price: float) -> None:
        """Устанавливает цену с проверкой корректности значения."""
        if new_price <= 0:
            print("Цена не должна быть нулевая или отрицательная")
            return
        if new_price < self.__price:
            answer = input(
                "Цена понижается. Подтвердите действие (y/n): "
            )
            if answer.lower() != "y":
                return
        self.__price = new_price

    @classmethod
    def new_product(
        cls,
        product_data: Dict[str, Any],
        products: Optional[List["Product"]] = None,
    ) -> "Product":
        """Создаёт товар из словаря с данными.

        Если передан список products и в нём есть товар с тем же
        названием, количество складывается со старым, а из двух
        цен выбирается более высокая. Иначе создаётся новый товар.
        """
        if products:
            for existing in products:
                if existing.name == product_data["name"]:
                    existing.quantity += product_data["quantity"]
                    if product_data["price"] > existing.price:
                        existing.price = product_data["price"]
                    return existing
        return cls(
            name=product_data["name"],
            description=product_data["description"],
            price=product_data["price"],
            quantity=product_data["quantity"],
        )


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
        self._products: List[Product] = (
            products if products is not None else []
        )
        Category.category_count += 1
        Category.product_count += len(self._products)

    def add_product(self, product: Product) -> None:
        """Добавляет товар в категорию и обновляет счётчик товаров."""
        self._products.append(product)
        Category.product_count += 1

    @property
    def products(self) -> str:
        """Возвращает список товаров категории в виде строк."""
        lines: List[str] = []
        for product in self._products:
            lines.append(
                f"{product.name}, {product.price} руб. "
                f"Остаток: {product.quantity} шт.\n"
            )
        return "".join(lines)


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

    description_phones = (
        "Смартфоны, как средство не только коммуникации, "
        "но и получение дополнительных функций для удобства жизни"
    )
    category1 = Category(
        "Смартфоны",
        description_phones,
        [product1, product2, product3],
    )

    print(category1.products)

    product4 = Product(
        "55\" QLED 4K",
        "Фоновая подсветка",
        123000.0,
        7,
    )
    category1.add_product(product4)

    print(category1.products)
    print(category1.product_count)

    new_product = Product.new_product(
        {
            "name": "Samsung Galaxy S23 Ultra",
            "description": "256GB, Серый цвет, 200MP камера",
            "price": 180000.0,
            "quantity": 5,
        }
    )
    print(new_product.name)
    print(new_product.description)
    print(new_product.price)
    print(new_product.quantity)

    new_product.price = 800
    print(new_product.price)

    new_product.price = -100
    print(new_product.price)

    new_product.price = 0
    print(new_product.price)
