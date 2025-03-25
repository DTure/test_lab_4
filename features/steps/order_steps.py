from behave import given, when, then
from app.eshop import Order, ShoppingCart, Product

@given("An empty shopping cart for order")
def empty_cart_for_order(context):
    context.cart = ShoppingCart()

@given("A product with name {product_name} and availability of {availability}")
def create_product_for_order(context, product_name, availability):
    context.product = Product(name=product_name, price=100.0, available_amount=int(availability))

@when("I add product to the shopping cart for order with amount {amount}")
def add_product_to_cart_for_order(context, amount):
    try:
        context.cart.add_product(context.product, int(amount))
    except ValueError as e:
        context.error = e  

@when("I place the order")
def place_order(context):
    context.order = Order()
    context.order.cart = context.cart
    context.order.place_order()

@then("The shopping cart is empty after order")
def check_cart_empty_after_order(context):
    assert len(context.cart.products) == 0

@then("The shopping cart contains the product after order")
def check_product_in_cart_after_order(context):
    assert hasattr(context, 'error'), "Expected an error due to insufficient availability"
    assert str(context.error) == f'Product {context.product} has only {context.product.available_amount} items', "Unexpected error message"
