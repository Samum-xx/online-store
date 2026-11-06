"""Тесты классов Product и Category с магическими методами."""
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
