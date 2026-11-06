"""Ядро e-commerce: сущности «Продукт» и «Категория» + загрузка JSON."""
import json
from typing import Any, Dict, Iterator, List, Optional


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
        self._price = price
        self.quantity = quantity

    def __str__(self) -> str:
        """Возвращает строковое представление товара."""
        return f"{self.name}, {self._price} руб. Остаток: {self.quantity} шт."

    def __add__(self, other: "Product") -> float:
        """Возвращает полную стоимость товаров двух объектов на складе."""
        if not isinstance(other, Product):
            raise TypeError(
                "Складывать можно только объекты класса Product"
            )
        return self.price * self.quantity + other.price * other.quantity

    @property
    def price(self) -> float:
        """Возвращает текущую цену товара."""
        return self._price

    @price.setter
    def price(self, new_price: float) -> None:
        """Устанавливает цену с проверкой корректности значения."""
        if new_price <= 0:
            print("Цена не должна быть нулевая или отрицательная")
            return
        if new_price < self._price:
            answer = input(
                "Цена понижается. Подтвердите действие (y/n): "
            )
            if answer.lower() != "y":
                return
        self._price = new_price

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

    def __str__(self) -> str:
        """Возвращает строку с общим количеством товаров на складе."""
        total = sum(product.quantity for product in self._products)
        return f"{self.name}, количество продуктов: {total} шт."

    def add_product(self, product: Product) -> None:
        """Добавляет товар в категорию и обновляет счётчик товаров."""
        self._products.append(product)
        Category.product_count += 1

    @property
    def products(self) -> str:
        """Возвращает список товаров категории в виде строк."""
        return "".join(
            f"{product}\n" for product in self._products
        )

    def __iter__(self) -> Iterator[Product]:
        """Возвращает итератор по товарам категории."""
        return CategoryIterator(self)


class CategoryIterator:
    """Вспомогательный класс для перебора товаров категории в цикле."""

    def __init__(self, category: Category) -> None:
        self._category = category
        self._index = 0

    def __iter__(self) -> "CategoryIterator":
        """Возвращает сам объект как итератор."""
        return self

    def __next__(self) -> Product:
        """Возвращает очередной товар категории."""
        products = self._category._products
        if self._index < len(products):
            product = products[self._index]
            self._index += 1
            return product
        raise StopIteration


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

    print(str(product1))
    print(str(product2))
    print(str(product3))

    description_phones = (
        "Смартфоны, как средство не только коммуникации, "
        "но и получение дополнительных функций для удобства жизни"
    )
    category1 = Category(
        "Смартфоны",
        description_phones,
        [product1, product2, product3],
    )

    print(str(category1))

    print(category1.products)

    print(product1 + product2)
    print(product1 + product3)
    print(product2 + product3)

    for product in category1:
        print(product)
