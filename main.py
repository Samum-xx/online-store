"""Ядро e-commerce: абстрактный продукт, миксин и категории."""
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional


class CreationLoggerMixin:
    """Миксин: при создании объекта печатает его параметры в консоль."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        print(repr(self))

    def __repr__(self) -> str:
        """Возвращает строку вида Класс('имя', 'описание', цена, кол-во)."""
        return (
            f"{type(self).__name__}('{self.name}', '{self.description}', "
            f"{self.price}, {self.quantity})"
        )


class BaseProduct(ABC):
    """Абстрактный базовый класс, общий для всех продуктов."""

    @abstractmethod
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
        return f"{self.name}, {self.price} руб. Остаток: {self.quantity} шт."

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


class Product(CreationLoggerMixin, BaseProduct):
    """Конкретный товар: сложение и фабрика создания из словаря."""

    def __init__(
        self,
        name: str,
        description: str,
        price: float,
        quantity: int,
    ) -> None:
        if quantity == 0:
            raise ValueError(
                "Товар с нулевым количеством не может быть добавлен"
            )
        super().__init__(name, description, price, quantity)

    def __add__(self, other: "Product") -> float:
        """Возвращает полную стоимость товаров двух объектов.

        Складывать можно только товары одного класса: смартфон
        со смартфоном, траву с травой и так далее. Попытка сложить
        товары разных классов или товар с не-товаром — TypeError.
        """
        if not isinstance(other, Product):
            raise TypeError(
                "Складывать можно только объекты класса Product"
            )
        if type(self) is not type(other):
            raise TypeError(
                "Складывать можно только товары одинакового класса"
            )
        return self.price * self.quantity + other.price * other.quantity

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


class Smartphone(Product):
    """Смартфон: товар с характеристиками производительности."""

    def __init__(
        self,
        name: str,
        description: str,
        price: float,
        quantity: int,
        efficiency: float,
        model: str,
        memory: int,
        color: str,
    ) -> None:
        super().__init__(name, description, price, quantity)
        self.efficiency = efficiency
        self.model = model
        self.memory = memory
        self.color = color


class LawnGrass(Product):
    """Газонная трава: товар со страной-производителем и сроком всхода."""

    def __init__(
        self,
        name: str,
        description: str,
        price: float,
        quantity: int,
        country: str,
        germination_period: str,
        color: str,
    ) -> None:
        super().__init__(name, description, price, quantity)
        self.country = country
        self.germination_period = germination_period
        self.color = color


class Category:
    """Категория товаров со статистикой по всем категориям."""

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
        """Добавляет товар в категорию.

        Принимает только объекты Product и его наследников.
        """
        if not isinstance(product, Product):
            raise TypeError(
                "Добавлять можно только объекты класса Product "
                "или его наследников"
            )
        self._products.append(product)
        Category.product_count += 1

    def middle_price(self) -> float:
        """Возвращает среднюю цену товаров категории.

        Если в категории нет товаров, возвращает ноль.
        """
        try:
            return (
                sum(product.price for product in self._products)
                / len(self._products)
            )
        except ZeroDivisionError:
            return 0.0

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
    """Вспомогательный класс для перебора товаров категории."""

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
    try:
        product_invalid = Product(
            "Бракованный товар", "Неверное количество", 1000.0, 0
        )
    except ValueError:
        print(
            "Возникла ошибка ValueError прерывающая работу программы "
            "при попытке добавить продукт с нулевым количеством"
        )
    else:
        print(
            "Не возникла ошибка ValueError при попытке добавить "
            "продукт с нулевым количеством"
        )

    product1 = Product(
        "Samsung Galaxy S23 Ultra",
        "256GB, Серый цвет, 200MP камера",
        180000.0,
        5,
    )
    product2 = Product(
        "Iphone 15",
        "512GB, Gray space",
        210000.0,
        8,
    )
    product3 = Product(
        "Xiaomi Redmi Note 11",
        "1024GB, Синий",
        31000.0,
        14,
    )

    category1 = Category(
        "Смартфоны",
        "Категория смартфонов",
        [product1, product2, product3],
    )

    print(category1.middle_price())

    category_empty = Category(
        "Пустая категория", "Категория без продуктов", []
    )
    print(category_empty.middle_price())
