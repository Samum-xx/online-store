"""Ядро e-commerce: продукты, категории и загрузка JSON."""
import json
from typing import Any, Dict, Iterator, List, Optional


class Product:
    """Базовый класс товара: название, описание, цена, количество."""

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
    smartphone1 = Smartphone(
        "Samsung Galaxy S23 Ultra",
        "256GB, Серый цвет, 200MP камера",
        180000.0,
        5,
        95.5,
        "S23 Ultra",
        256,
        "Серый",
    )
    smartphone2 = Smartphone(
        "Iphone 15",
        "512GB, Gray space",
        210000.0,
        8,
        98.2,
        "15",
        512,
        "Gray space",
    )
    smartphone3 = Smartphone(
        "Xiaomi Redmi Note 11",
        "1024GB, Синий",
        31000.0,
        14,
        90.3,
        "Note 11",
        1024,
        "Синий",
    )

    print(smartphone1.name)
    print(smartphone1.description)
    print(smartphone1.price)
    print(smartphone1.quantity)
    print(smartphone1.efficiency)
    print(smartphone1.model)
    print(smartphone1.memory)
    print(smartphone1.color)

    print(smartphone2.name)
    print(smartphone2.description)
    print(smartphone2.price)
    print(smartphone2.quantity)
    print(smartphone2.efficiency)
    print(smartphone2.model)
    print(smartphone2.memory)
    print(smartphone2.color)

    print(smartphone3.name)
    print(smartphone3.description)
    print(smartphone3.price)
    print(smartphone3.quantity)
    print(smartphone3.efficiency)
    print(smartphone3.model)
    print(smartphone3.memory)
    print(smartphone3.color)

    grass1 = LawnGrass(
        "Газонная трава",
        "Элитная трава для газона",
        500.0,
        20,
        "Россия",
        "7 дней",
        "Зеленый",
    )
    grass2 = LawnGrass(
        "Газонная трава 2",
        "Выносливая трава",
        450.0,
        15,
        "США",
        "5 дней",
        "Темно-зеленый",
    )

    print(grass1.name)
    print(grass1.description)
    print(grass1.price)
    print(grass1.quantity)
    print(grass1.country)
    print(grass1.germination_period)
    print(grass1.color)

    print(grass2.name)
    print(grass2.description)
    print(grass2.price)
    print(grass2.quantity)
    print(grass2.country)
    print(grass2.germination_period)
    print(grass2.color)

    smartphone_sum = smartphone1 + smartphone2
    print(smartphone_sum)

    grass_sum = grass1 + grass2
    print(grass_sum)

    try:
        invalid_sum = smartphone1 + grass1
    except TypeError:
        print("Возникла ошибка TypeError при попытке сложения")
    else:
        print("Не возникла ошибка TypeError при попытке сложения")

    category_smartphones = Category(
        "Смартфоны",
        "Высокотехнологичные смартфоны",
        [smartphone1, smartphone2],
    )
    category_grass = Category(
        "Газонная трава",
        "Различные виды газонной травы",
        [grass1, grass2],
    )

    category_smartphones.add_product(smartphone3)

    print(category_smartphones.products)

    print(Category.product_count)

    try:
        category_smartphones.add_product("Not a product")
    except TypeError:
        print("Возникла ошибка TypeError при добавлении не продукта")
    else:
        print("Не возникла ошибка TypeError при добавлении не продукта")
