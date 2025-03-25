from behave import given, when, then
from app.eshop import Product

@given("The product with name {product_name} has availability of {availability}")
def create_product(context, product_name, availability):
    context.product = Product(name=product_name, price=123, available_amount=int(availability))

@when("I check if product is available in amount {product_amount}")
def check_product_availability(context, product_amount):
    try:
        context.product_available = context.product.is_available(int(product_amount))
    except (ValueError, TypeError):
        context.product_available = False

@then("Product is available")
def product_is_available(context):
    assert context.product_available == True

@then("Product is not available")
def product_is_not_available(context):
    assert context.product_available == False
