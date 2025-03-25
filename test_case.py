import unittest
from unittest.mock import MagicMock
from app.eshop import Product, ShoppingCart, Order

class TestEshop(unittest.TestCase):
    def setUp(self):
        self.product = Product(name='Test', price=123.45, available_amount=21)
        self.cart = ShoppingCart()
        self.mock_shipping_service = MagicMock()
        self.mock_shipping_service.create_shipping.return_value = "fake_shipping_id"     
        self.order = Order(cart=self.cart, shipping_service=self.mock_shipping_service)
    
    def tearDown(self):
        self.cart = ShoppingCart()
    
    # Tests for class Product
    def test_is_available(self):
        self.assertTrue(self.product.is_available(10), 'Продукт має бути доступний')
        self.assertFalse(self.product.is_available(30), 'Продукт має бути недоступний')
    
    def test_product_equality(self):
        product2 = Product(name='Test', price=123.45, available_amount=21)
        self.assertEqual(self.product, product2, 'Продукти з однаковими іменами повинні бути рівними')
    
    def test_product_inequality(self):
        product2 = Product(name='Test2', price=123.45, available_amount=21)
        self.assertNotEqual(self.product, product2, 'Продукти з різними іменами повинні бути нерівними')
    
    def test_product_hash(self):
        product2 = Product(name='Test', price=123.45, available_amount=21)
        self.assertEqual(hash(self.product), hash(product2), 'Хеш-значення продуктів з однаковими іменами повинні бути рівними')
    
    def test_product_buy(self):
        initial_amount = self.product.available_amount
        self.product.buy(10)
        self.assertEqual(self.product.available_amount, initial_amount - 10, 'Кількість продукту повинна бути зменшена після покупки')
    
    # Tests for class ShoppingCart 
    def test_add_product_to_cart(self):
        self.cart.add_product(self.product, 10)
        self.assertTrue(self.cart.contains_product(self.product), 'Продукт повинен бути в корзині')
    
    def test_add_unavailable_product(self):
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, 30)
    
    def test_remove_product_from_cart(self):
        self.cart.add_product(self.product, 10)
        self.cart.remove_product(self.product)
        self.assertFalse(self.cart.contains_product(self.product), 'Продукт повинен бути видалений з корзини')
    
    def test_calculate_total(self):
        self.cart.add_product(self.product, 10)
        total = self.cart.calculate_total()
        self.assertEqual(total, 1234.5, 'Загальна вартість повинна бути правильно розрахована')
    
    def test_submit_cart_order(self):
        self.cart.add_product(self.product, 10)
        self.cart.submit_cart_order()
        self.assertEqual(self.product.available_amount, 11, 'Кількість продукту повинна бути зменшена')
        self.assertEqual(len(self.cart.products), 0, 'Корзина повинна бути порожньою')
    
    # Tests for class Order
    def test_place_order(self):
        self.cart.add_product(self.product, 10)
        self.order.place_order(shipping_type="standard") 
        self.assertEqual(self.product.available_amount, 11, 'Кількість продукту повинна бути зменшена')
        self.assertEqual(len(self.cart.products), 0, 'Корзина повинна бути порожньою')

if __name__ == '__main__':
    unittest.main()