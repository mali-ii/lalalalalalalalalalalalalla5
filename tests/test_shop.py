import unittest

from shop import (
    add_to_cart,
    cart_total,
    get_low_stock,
    remove_from_cart,
    search_advanced,
    total_sum,
    update_quantity,
)


class TestGetLowStock(unittest.TestCase):
    def test_empty_list(self):
        self.assertEqual(get_low_stock([]), [])

    def test_no_low_stock(self):
        self.assertEqual(get_low_stock([{"name": "A", "sizes": {40: 10}}]), [])

    def test_one_low_stock(self):
        products = [
            {"name": "A", "sizes": {40: 1}},
            {"name": "B", "sizes": {40: 10}},
        ]
        result = get_low_stock(products)
        self.assertEqual([p["name"] for p in result], ["A"])

    def test_sums_all_sizes_and_sorts(self):
        products = [
            {"name": "B", "sizes": {40: 2, 41: 1}},
            {"name": "A", "sizes": {40: 1}},
        ]
        self.assertEqual([p["name"] for p in get_low_stock(products)], ["A", "B"])


class TestSearchAdvanced(unittest.TestCase):
    def setUp(self):
        self.products = [
            {"name": "Кроссовки Air", "brand": "Nike", "category": "Обувь", "price": 9000},
            {"name": "Кроссовки Run", "brand": "Asics", "category": "Обувь", "price": 7000},
            {"name": "Футболка", "brand": "Nike", "category": "Одежда", "price": 3000},
        ]

    def test_search_by_name(self):
        result = search_advanced(self.products, "air")
        self.assertEqual([p["name"] for p in result], ["Кроссовки Air"])

    def test_search_by_brand_case_insensitive(self):
        self.assertEqual(len(search_advanced(self.products, "NIKE")), 2)

    def test_filter_by_category(self):
        result = search_advanced(self.products, "кроссовки", category="Обувь")
        self.assertEqual(len(result), 2)

    def test_filter_by_price(self):
        result = search_advanced(self.products, "кроссовки", min_price=7000, max_price=8000)
        self.assertEqual([p["name"] for p in result], ["Кроссовки Run"])


class TestTotalSum(unittest.TestCase):
    def test_empty_cart(self):
        self.assertEqual(total_sum([]), 0)

    def test_products_with_quantities(self):
        self.assertEqual(total_sum([{"price": 100, "quantity": 2}, {"price": 50}]), 250)


class TestAddToCart(unittest.TestCase):
    def setUp(self):
        self.products = [{"id": 1, "name": "A", "price": 100, "sizes": {40: 5}}]
        self.cart = []

    def test_invalid_size(self):
        result, message = add_to_cart(self.cart, self.products, 1, 99, 1)
        self.assertFalse(result)
        self.assertIn("размер", message.lower())

    def test_successful_addition(self):
        result, _ = add_to_cart(self.cart, self.products, 1, 40, 2)
        self.assertTrue(result)
        self.assertEqual(self.cart[0]["quantity"], 2)

    def test_repeated_addition_increases_quantity(self):
        add_to_cart(self.cart, self.products, 1, 40, 1)
        result, _ = add_to_cart(self.cart, self.products, 1, 40, 2)
        self.assertTrue(result)
        self.assertEqual(len(self.cart), 1)
        self.assertEqual(self.cart[0]["quantity"], 3)


class TestRemoveFromCart(unittest.TestCase):
    def test_remove_existing_item(self):
        cart = [{"id": 1, "size": 40, "price": 100, "quantity": 1}]
        self.assertTrue(remove_from_cart(cart, 1, 40))
        self.assertEqual(cart, [])

    def test_missing_item_returns_false(self):
        self.assertFalse(remove_from_cart([], 1, 40))


class TestUpdateQuantity(unittest.TestCase):
    def test_updates_existing_item(self):
        cart = [{"id": 1, "size": 40, "price": 100, "quantity": 1}]
        self.assertTrue(update_quantity(cart, 1, 40, 4))
        self.assertEqual(cart[0]["quantity"], 4)

    def test_rejects_nonpositive_quantity(self):
        cart = [{"id": 1, "size": 40, "price": 100, "quantity": 1}]
        self.assertFalse(update_quantity(cart, 1, 40, 0))
        self.assertEqual(cart[0]["quantity"], 1)


class TestCartTotal(unittest.TestCase):
    def test_empty_cart_total(self):
        self.assertEqual(cart_total([]), 0)

    def test_total_includes_quantities(self):
        self.assertEqual(cart_total([{"price": 250, "quantity": 3}, {"price": 100}]), 850)


class TestExpectedError(unittest.TestCase):
    def test_division_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            _ = 1 / 0


if __name__ == "__main__":
    unittest.main()
