from behave import given, when, then
from app.eshop import Product, ShoppingCart

@given("The product has availability of {availability}")
def create_product_for_cart(context, availability):
    context.product = Product(name="any", price=123, available_amount=int(availability))

@given("An empty shopping cart")
def empty_cart(context):
    context.cart = ShoppingCart()

@when("I add product to the cart in amount {product_amount}")
def add_product(context, product_amount):
    try:
        context.cart.add_product(context.product, int(product_amount))
        context.add_successfully = True
    except (ValueError, TypeError):
        context.add_successfully = False

@then("Product is added to the cart successfully")
def add_successful(context):
    assert context.add_successfully == True

@then("Product is not added to cart successfully")
def add_failed(context):
    assert context.add_successfully == False

@then("The total price should be calculated correctly")
def check_total_price(context):
    total = context.cart.calculate_total()
    expected_total = context.product.price * 5 
    assert total == expected_total, f"Expected {expected_total}, but got {total}"

@when("I remove product from the cart")
def remove_product(context):
    context.cart.remove_product(context.product)

@then("The cart should be empty")
def check_cart_empty(context):
    assert len(context.cart.products) == 0

@when('I add invalid amount to the cart')
def add_invalid_amount(context):
    try:
        context.cart.add_product(context.product, "invalid")
        context.add_successfully = False
    except (ValueError, TypeError):
        context.add_successfully = False

@then("Product is not added to cart due to invalid amount")
def add_failed_invalid(context):
    assert context.add_successfully == False

@when("I add another product to the cart in amount 2")
def step_impl(context):
    another_product = Product(name="Product2", price=15, available_amount=10)
    context.cart.add_product(another_product, 2)  

