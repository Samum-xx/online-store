"""Тесты инициализации классов Product и Category."""
import pytest

from main import Category, Product, load_products_from_json


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


class TestProduct:
    def test_initialization(self, product_one):
        assert product_one.name == "Samsung Galaxy S23 Ultra"
        assert product_one.description == "256GB, Серый цвет"
        assert product_one.price == 180000.0
        assert product_one.quantity == 5

    def test_price_is_float(self, product_one):
        assert isinstance(product_one.price, float)

    def test_quantity_is_int(self, product_one):
        assert isinstance(product_one.quantity, int)

    def test_string_fields_are_str(self, product_one):
        assert isinstance(product_one.name, str)
        assert isinstance(product_one.description, str)


class TestCategory:
    def test_initialization(self, product_one):
        category = Category(
            "Смартфоны",
            "Смартфоны разных производителей",
            [product_one],
        )
        assert category.name == "Смартфоны"
        assert category.description == "Смартфоны разных производителей"
        assert isinstance(category.products, list)

    def test_products_list_contains_product_objects(
        self, product_one, product_two
    ):
        category = Category(
            "Смартфоны",
            "Описание",
            [product_one, product_two],
        )
        assert all(isinstance(item, Product) for item in category.products)

    def test_products_default_to_empty_list(self):
        category = Category("Пустая", "Без товаров")
        assert category.products == []

    def test_category_count_increments(self, product_one):
        assert Category.category_count == 0
        Category("Смартфоны", "Описание", [product_one])
        assert Category.category_count == 1
        Category("Телевизоры", "Описание", [])
        assert Category.category_count == 2

    def test_product_count_increments(self, product_one, product_two):
        assert Category.product_count == 0
        Category("Смартфоны", "Описание", [product_one, product_two])
        assert Category.product_count == 2
        Category("Телевизоры", "Описание", [product_one])
        assert Category.product_count == 3

    def test_empty_category_counts(self):
        Category("Пустая", "Без товаров", [])
        assert Category.category_count == 1
        assert Category.product_count == 0

    def test_counters_are_class_attributes(self, product_one):
        category = Category("Смартфоны", "Описание", [product_one])
        assert category.category_count == Category.category_count
        assert category.product_count == Category.product_count


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
        assert result[0].products[0].name == "Iphone 15"
        assert result[0].products[0].price == 210000.0
        assert result[0].products[0].quantity == 8

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
        assert result[1].products == []

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
        assert len(result[0].products) == 3
        assert result[1].name == "Телевизоры"
        assert result[1].products[0].name == "55\" QLED 4K"
