"""Тесты классов Product, Category и их наследников."""
import pytest

from main import (
    BaseProduct,
    Category,
    CreationLoggerMixin,
    LawnGrass,
    Product,
    Smartphone,
    load_products_from_json,
)


@pytest.fixture(autouse=True)
def reset_counters():
    """Сбрасывает счётчики класса перед каждым тестом."""
    Category.category_count = 0
    Category.product_count = 0
    yield


@pytest.fixture
def product_one() -> Product:
    return Product(
        "Samsung Galaxy S23 Ultra",
        "256GB, Серый цвет",
        180000.0,
        5,
    )


@pytest.fixture
def product_two() -> Product:
    return Product(
        "Iphone 15",
        "512GB, Gray space",
        210000.0,
        8,
    )


@pytest.fixture
def empty_category() -> Category:
    return Category("Пустая", "Без товаров")


class TestProduct:
    def test_initialization(self, product_one):
        assert product_one.name == "Samsung Galaxy S23 Ultra"
        assert product_one.description == "256GB, Серый цвет"
        assert product_one.quantity == 5

    def test_price_is_float(self, product_one):
        assert isinstance(product_one.price, float)

    def test_quantity_is_int(self, product_one):
        assert isinstance(product_one.quantity, int)

    def test_string_fields_are_str(self, product_one):
        assert isinstance(product_one.name, str)
        assert isinstance(product_one.description, str)

    def test_price_getter_returns_value(self, product_one):
        assert product_one.price == 180000.0

    def test_price_attribute_is_private(self, product_one):
        assert "price" not in product_one.__dict__
        assert "_price" in product_one.__dict__

    def test_setter_updates_positive_price(self, product_one):
        product_one.price = 200000.0
        assert product_one.price == 200000.0

    def test_setter_rejects_negative(self, product_one, capsys):
        product_one.price = -100
        captured = capsys.readouterr()
        assert (
            "Цена не должна быть нулевая или отрицательная"
            in captured.out
        )
        assert product_one.price == 180000.0

    def test_setter_rejects_zero(self, product_one, capsys):
        product_one.price = 0
        captured = capsys.readouterr()
        assert (
            "Цена не должна быть нулевая или отрицательная"
            in captured.out
        )
        assert product_one.price == 180000.0

    def test_price_decrease_confirmed(self, product_one, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda *args: "y")
        product_one.price = 150000.0
        assert product_one.price == 150000.0

    def test_price_decrease_cancelled(self, product_one, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda *args: "n")
        product_one.price = 150000.0
        assert product_one.price == 180000.0

    def test_new_product_creates_instance(self):
        data = {
            "name": "Iphone 15",
            "description": "512GB, Gray space",
            "price": 210000.0,
            "quantity": 8,
        }
        product = Product.new_product(data)
        assert isinstance(product, Product)
        assert product.name == "Iphone 15"
        assert product.price == 210000.0
        assert product.quantity == 8

    def test_new_product_merges_duplicate(self, product_one):
        data = {
            "name": "Samsung Galaxy S23 Ultra",
            "description": "Другое описание",
            "price": 200000.0,
            "quantity": 3,
        }
        result = Product.new_product(data, [product_one])
        assert result is product_one
        assert result.quantity == 8
        assert result.price == 200000.0

    def test_new_product_keeps_higher_price(self, product_one):
        data = {
            "name": "Samsung Galaxy S23 Ultra",
            "description": "Другое описание",
            "price": 100000.0,
            "quantity": 3,
        }
        result = Product.new_product(data, [product_one])
        assert result is product_one
        assert result.quantity == 8
        assert result.price == 180000.0

    def test_product_str(self, product_one):
        assert str(product_one) == (
            "Samsung Galaxy S23 Ultra, 180000.0 руб. Остаток: 5 шт."
        )


class TestCategory:
    def test_initialization(self, product_one):
        category = Category(
            "Смартфоны",
            "Смартфоны разных производителей",
            [product_one],
        )
        assert category.name == "Смартфоны"
        assert category.description == "Смартфоны разных производителей"
        assert "Samsung Galaxy S23 Ultra" in category.products

    def test_products_attribute_is_private(self, product_one):
        category = Category("Смартфоны", "Описание", [product_one])
        assert "products" not in category.__dict__
        assert "_products" in category.__dict__

    def test_products_getter_returns_string(self, product_one):
        category = Category("Смартфоны", "Описание", [product_one])
        assert isinstance(category.products, str)

    def test_products_getter_format(self, product_one):
        category = Category("Смартфоны", "Описание", [product_one])
        expected = (
            "Samsung Galaxy S23 Ultra, 180000.0 руб. "
            "Остаток: 5 шт.\n"
        )
        assert category.products == expected

    def test_products_getter_empty(self, empty_category):
        assert empty_category.products == ""

    def test_products_getter_multiple(self, product_one, product_two):
        category = Category(
            "Смартфоны",
            "Описание",
            [product_one, product_two],
        )
        assert "Samsung Galaxy S23 Ultra" in category.products
        assert "Iphone 15" in category.products
        assert "Остаток: 8 шт." in category.products

    def test_add_product_appends(self, empty_category, product_one):
        empty_category.add_product(product_one)
        assert "Samsung Galaxy S23 Ultra" in empty_category.products

    def test_add_product_updates_counter(
        self, empty_category, product_one
    ):
        assert Category.product_count == 0
        empty_category.add_product(product_one)
        assert Category.product_count == 1

    def test_category_count_increments(self):
        assert Category.category_count == 0
        Category("Смартфоны", "Описание")
        assert Category.category_count == 1
        Category("Телевизоры", "Описание")
        assert Category.category_count == 2

    def test_product_count_increments(self, product_one, product_two):
        assert Category.product_count == 0
        Category("Смартфоны", "Описание", [product_one, product_two])
        assert Category.product_count == 2
        Category("Телевизоры", "Описание", [product_one])
        assert Category.product_count == 3

    def test_empty_category_counts(self, empty_category):
        assert Category.category_count == 1
        assert Category.product_count == 0

    def test_category_str_counts_total_quantity(
        self, product_one, product_two
    ):
        category = Category(
            "Смартфоны",
            "Описание",
            [product_one, product_two],
        )
        assert str(category) == "Смартфоны, количество продуктов: 13 шт."

    def test_category_str_empty(self, empty_category):
        assert str(empty_category) == (
            "Пустая, количество продуктов: 0 шт."
        )

    def test_category_str_after_add_product(
        self, empty_category, product_one
    ):
        empty_category.add_product(product_one)
        assert "количество продуктов: 5 шт." in str(empty_category)

    def test_iterate_over_category(self, product_one, product_two):
        category = Category(
            "Смартфоны",
            "Описание",
            [product_one, product_two],
        )
        items = [product for product in category]
        assert items == [product_one, product_two]

    def test_iterator_returns_products_in_order(
        self, product_one, product_two
    ):
        category = Category(
            "Смартфоны",
            "Описание",
            [product_one, product_two],
        )
        iterator = iter(category)
        assert next(iterator) is product_one
        assert next(iterator) is product_two
        with pytest.raises(StopIteration):
            next(iterator)

    def test_iterator_empty_category(self, empty_category):
        assert list(empty_category) == []

    def test_iterator_protocol_direct(self, product_one):
        category = Category("Смартфоны", "Описание", [product_one])
        iterator = iter(category)
        assert iter(iterator) is iterator
        assert list(iterator) == [product_one]


class TestAdd:
    def test_add_returns_total_value(self, product_one, product_two):
        assert product_one + product_two == 180000.0 * 5 + 210000.0 * 8

    def test_add_is_commutative(self, product_one, product_two):
        assert product_one + product_two == product_two + product_one

    def test_add_rejects_non_product(self, product_one):
        with pytest.raises(TypeError):
            product_one + 100


def make_json(content: str, tmp_path):
    filepath = tmp_path / "products.json"
    filepath.write_text(content.strip(), encoding="utf-8")
    return str(filepath)


class TestLoadFromJson:
    def test_load_categories(self, tmp_path):
        content = """
        [
            {
                "name": "Смартфоны",
                "description": "Описание",
                "products": [
                    {
                        "name": "Iphone 15",
                        "description": "512GB",
                        "price": 210000.0,
                        "quantity": 8
                    }
                ]
            }
        ]
        """
        path = make_json(content, tmp_path)
        result = load_products_from_json(path)
        assert len(result) == 1
        assert result[0].name == "Смартфоны"
        assert "Iphone 15" in result[0].products
        assert "210000.0 руб." in result[0].products

    def test_load_multiple_categories(self, tmp_path):
        content = """
        [
            {
                "name": "Смартфоны",
                "description": "Описание",
                "products": [
                    {
                        "name": "Iphone 15",
                        "description": "512GB",
                        "price": 210000.0,
                        "quantity": 8
                    }
                ]
            },
            {
                "name": "Телевизоры",
                "description": "Описание ТВ",
                "products": []
            }
        ]
        """
        path = make_json(content, tmp_path)
        result = load_products_from_json(path)
        assert len(result) == 2
        assert result[1].products == ""

    def test_load_updates_counters(self, tmp_path):
        content = """
        [
            {
                "name": "Смартфоны",
                "description": "Описание",
                "products": [
                    {
                        "name": "Iphone 15",
                        "description": "512GB",
                        "price": 210000.0,
                        "quantity": 8
                    },
                    {
                        "name": "Xiaomi",
                        "description": "1024GB",
                        "price": 31000.0,
                        "quantity": 14
                    }
                ]
            }
        ]
        """
        path = make_json(content, tmp_path)
        load_products_from_json(path)
        assert Category.category_count == 1
        assert Category.product_count == 2

    def test_load_real_file(self):
        result = load_products_from_json("products.json")
        assert len(result) == 2
        assert result[0].name == "Смартфоны"
        assert "Samsung Galaxy S23 Ultra" in result[0].products
        assert "Iphone 15" in result[0].products
        assert "Xiaomi Redmi Note 11" in result[0].products
        assert result[1].name == "Телевизоры"
        assert '55" QLED 4K' in result[1].products


class TestInheritance:
    def test_smartphone_is_subclass(self):
        assert issubclass(Smartphone, Product)

    def test_lawn_grass_is_subclass(self):
        assert issubclass(LawnGrass, Product)

    def test_smartphone_attributes(self):
        smartphone = Smartphone(
            "Iphone 15",
            "512GB, Gray space",
            210000.0,
            8,
            98.2,
            "15",
            512,
            "Gray space",
        )
        assert smartphone.name == "Iphone 15"
        assert smartphone.description == "512GB, Gray space"
        assert smartphone.price == 210000.0
        assert smartphone.quantity == 8
        assert smartphone.efficiency == 98.2
        assert smartphone.model == "15"
        assert smartphone.memory == 512
        assert smartphone.color == "Gray space"

    def test_lawn_grass_attributes(self):
        grass = LawnGrass(
            "Газонная трава",
            "Элитная трава для газона",
            500.0,
            20,
            "Россия",
            "7 дней",
            "Зеленый",
        )
        assert grass.name == "Газонная трава"
        assert grass.description == "Элитная трава для газона"
        assert grass.price == 500.0
        assert grass.quantity == 20
        assert grass.country == "Россия"
        assert grass.germination_period == "7 дней"
        assert grass.color == "Зеленый"

    def test_smartphone_str_inherited(self):
        smartphone = Smartphone(
            "Iphone 15", "512GB", 210000.0, 8, 98.2, "15", 512, "Gray"
        )
        assert str(smartphone) == (
            "Iphone 15, 210000.0 руб. Остаток: 8 шт."
        )

    def test_product_instance_of_subclasses(self):
        smartphone = Smartphone("A", "B", 1.0, 1, 1.0, "M", 1, "C")
        grass = LawnGrass("G", "D", 1.0, 1, "RU", "3", "Green")
        assert isinstance(smartphone, Product)
        assert isinstance(grass, Product)


class TestAddSameClassOnly:
    def test_add_same_subclass(self):
        smartphone1 = Smartphone("A", "B", 100.0, 10, 1.0, "M", 1, "C")
        smartphone2 = Smartphone("D", "E", 200.0, 2, 1.0, "N", 2, "F")
        assert smartphone1 + smartphone2 == 100.0 * 10 + 200.0 * 2

    def test_add_grass_same_class(self):
        grass1 = LawnGrass("A", "B", 500.0, 20, "RU", "7", "Green")
        grass2 = LawnGrass("C", "D", 450.0, 15, "US", "5", "Dark")
        assert grass1 + grass2 == 500.0 * 20 + 450.0 * 15

    def test_add_smartphone_and_grass_raises(self):
        smartphone = Smartphone("A", "B", 100.0, 10, 1.0, "M", 1, "C")
        grass = LawnGrass("G", "D", 500.0, 20, "RU", "7", "Green")
        with pytest.raises(TypeError):
            smartphone + grass

    def test_add_smartphone_and_product_raises(self):
        smartphone = Smartphone("A", "B", 100.0, 10, 1.0, "M", 1, "C")
        product = Product("P", "D", 100.0, 10)
        with pytest.raises(TypeError):
            smartphone + product

    def test_add_product_and_smartphone_raises(self):
        smartphone = Smartphone("A", "B", 100.0, 10, 1.0, "M", 1, "C")
        product = Product("P", "D", 100.0, 10)
        with pytest.raises(TypeError):
            product + smartphone

    def test_add_smartphone_and_number_raises(self):
        smartphone = Smartphone("A", "B", 100.0, 10, 1.0, "M", 1, "C")
        with pytest.raises(TypeError):
            smartphone + 100


class TestAddProductRestriction:
    def test_add_product_accepts_product(self, empty_category):
        product = Product("Товар", "Описание", 100.0, 3)
        empty_category.add_product(product)
        assert Category.product_count == 1
        assert "Товар" in empty_category.products

    def test_add_product_accepts_smartphone(self, empty_category):
        smartphone = Smartphone("A", "B", 100.0, 3, 1.0, "M", 1, "C")
        empty_category.add_product(smartphone)
        assert Category.product_count == 1

    def test_add_product_accepts_lawn_grass(self, empty_category):
        grass = LawnGrass("G", "D", 500.0, 5, "RU", "7", "Green")
        empty_category.add_product(grass)
        assert Category.product_count == 1

    def test_add_product_rejects_string(self, empty_category):
        with pytest.raises(TypeError):
            empty_category.add_product("Not a product")

    def test_add_product_rejects_number(self, empty_category):
        with pytest.raises(TypeError):
            empty_category.add_product(42)

    def test_add_product_rejects_none(self, empty_category):
        with pytest.raises(TypeError):
            empty_category.add_product(None)


class TestBaseProduct:
    def test_base_product_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            BaseProduct("Имя", "Описание", 100.0, 1)

    def test_product_is_subclass_of_base(self):
        assert issubclass(Product, BaseProduct)

    def test_smartphone_inherits_only_product(self):
        assert Smartphone.__bases__ == (Product,)

    def test_lawn_grass_inherits_only_product(self):
        assert LawnGrass.__bases__ == (Product,)

    def test_base_product_in_mro(self):
        assert BaseProduct in Product.__mro__

    def test_common_str_inherited_from_base(self):
        product = Product("Товар", "Описание", 100.0, 2)
        assert str(product) == "Товар, 100.0 руб. Остаток: 2 шт."


class TestCreationLoggerMixin:
    def test_mixin_in_mro(self):
        assert CreationLoggerMixin in Product.__mro__

    def test_creation_prints_product_info(self, capsys):
        product = Product("Товар", "Описание", 100.0, 2)
        captured = capsys.readouterr()
        assert (
            "Product('Товар', 'Описание', 100.0, 2)\n"
            in captured.out
        )
        assert product.name == "Товар"

    def test_repr_format(self):
        product = Product("Товар", "Описание", 100.0, 2)
        assert repr(product) == "Product('Товар', 'Описание', 100.0, 2)"

    def test_smartphone_creation_prints_class_name(self, capsys):
        smartphone = Smartphone("A", "B", 1.0, 1, 1.0, "M", 1, "C")
        captured = capsys.readouterr()
        assert "Smartphone(" in captured.out
        assert smartphone.name == "A"

    def test_grass_creation_prints_class_name(self, capsys):
        grass = LawnGrass("G", "D", 1.0, 1, "RU", "3", "Green")
        captured = capsys.readouterr()
        assert "LawnGrass(" in captured.out
        assert grass.country == "RU"
