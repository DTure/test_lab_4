import time
import uuid
import boto3
from app.eshop import Product, ShoppingCart, Order, Shipment
import random
from services import ShippingService
from services.repository import ShippingRepository
from services.publisher import ShippingPublisher
from datetime import datetime, timedelta, timezone
from services.config import AWS_ENDPOINT_URL, AWS_REGION, SHIPPING_QUEUE
import pytest


@pytest.mark.parametrize("order_id, shipping_id", [
    ("order_1", "shipping_1"),
    ("order_i2hur2937r9", "shipping_1!!!!"),
    (8662354, 123456),
    (str(uuid.uuid4()), str(uuid.uuid4()))
])

def test_place_order_with_mocked_repo(mocker, order_id, shipping_id):
    mock_repo = mocker.Mock()
    mock_publisher = mocker.Mock()
    shipping_service = ShippingService(mock_repo, mock_publisher)
    mock_repo.create_shipping.return_value = shipping_id
    cart = ShoppingCart()
    cart.add_product(Product(
        available_amount=10,
        name='Product',
        price=random.random() * 10000),
        amount=9
    )
    order = Order(cart, shipping_service, order_id)
    due_date = datetime.now(timezone.utc) + timedelta(seconds=3)
    actual_shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=due_date
    )
    assert actual_shipping_id == shipping_id, "Actual shipping id must be equal to mock return value"
    mock_repo.create_shipping.assert_called_with(ShippingService.list_available_shipping_type()[0], ["Product"], order_id, shipping_service.SHIPPING_CREATED, due_date)
    mock_publisher.send_new_shipping.assert_called_with(shipping_id)


def test_place_order_with_unavailable_shipping_type_fails(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()
    cart.add_product(Product(
        available_amount=10,
        name='Product',
        price=random.random() * 10000),
        amount=9
    )
    order = Order(cart, shipping_service)
    shipping_id = None
    with pytest.raises(ValueError) as excinfo:
        shipping_id = order.place_order(
            "Новий тип доставки",
            due_date=datetime.now(timezone.utc) + timedelta(seconds=3)
        )
    assert shipping_id is None, "Shipping id must not be assigned"
    assert "Shipping type is not available" in str(excinfo.value)

def test_when_place_order_then_shipping_in_queue(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()
    cart.add_product(Product(
        available_amount=10,
        name='Product',
        price=random.random() * 10000),
        amount=9
    )
    order = Order(cart, shipping_service)
    shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=datetime.now(timezone.utc) + timedelta(minutes=1)
    )
    sqs_client = boto3.client(
        "sqs",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION
    )
    queue_url = sqs_client.get_queue_url(QueueName=SHIPPING_QUEUE)["QueueUrl"]
    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10
    )
    messages = response.get("Messages", [])
    assert len(messages) == 1, "Expected 1 SQS message"
    body = messages[0]["Body"]
    assert shipping_id == body

# New test

def test_shipping_service_handles_invalid_data(mocker):
    mock_repo = mocker.Mock()
    mock_publisher = mocker.Mock()
    shipping_service = ShippingService(mock_repo, mock_publisher)
    
    with pytest.raises(ValueError, match="due datetime must be greater"):
        shipping_service.create_shipping(
            shipping_type="Нова Пошта",
            product_ids=["item1"],
            order_id="test-order",
            due_date=datetime.now(timezone.utc) - timedelta(days=1)  
        )
    
    mock_repo.create_shipping.side_effect = Exception("DB error")
    with pytest.raises(Exception, match="DB error"):
        shipping_service.create_shipping(
            shipping_type="Нова Пошта",
            product_ids=["item1"],
            order_id="test-order",
            due_date=datetime.now(timezone.utc) + timedelta(days=1)
        )
    mock_publisher.send_new_shipping.assert_not_called()  

def test_order_with_multiple_products(mocker):
    mock_repo = mocker.Mock()
    mock_repo.create_shipping.return_value = "test-shipping-id"
    shipping_service = ShippingService(mock_repo, mocker.Mock())
    
    cart = ShoppingCart()
    cart.add_product(Product("Product1", 50, 5), 1)
    cart.add_product(Product("Product2", 150, 3), 2)
    
    order = Order(cart, shipping_service)
    shipping_id = order.place_order("Укр Пошта")
    assert shipping_id == "test-shipping-id"

def test_order_fails_if_product_unavailable():
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()
    product = Product("Рідкісний товар", 999, 1)
    
    with pytest.raises(ValueError, match="has only 1 items"):
        cart.add_product(product, 2) 

def test_product_quantity_limits(dynamo_resource):
    product = Product("Унікальний товар", 100, 2)
    
    cart1 = ShoppingCart()
    cart1.add_product(product, 2) 

    cart2 = ShoppingCart()
    with pytest.raises(ValueError, match="has only 0 items"):
        cart2.add_product(product, 1)

def test_shipping_record_created_in_dynamodb(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()
    cart.add_product(Product("Книга", 299, 10), 1)
    
    order = Order(cart, shipping_service)
    shipping_id = order.place_order("Самовивіз")
    
    record = ShippingRepository().get_shipping(shipping_id)
    assert record["shipping_type"] == "Самовивіз"
    assert all(key in record for key in ["order_id", "created_date", "due_date"])
    assert record["order_id"] == order.order_id  

def test_shipping_status_updates_in_dynamodb(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    shipping_id = shipping_service.repository.create_shipping(
        "Нова Пошта", ["item1"], "test-order", "created", datetime.now(timezone.utc) + timedelta(days=1)
    )
    
    shipping_service.repository.update_shipping_status(shipping_id, "in progress")
    record = shipping_service.repository.get_shipping(shipping_id)
    assert record["shipping_status"] == "in progress"

def test_fail_shipping_when_due_date_passed(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    past_date = datetime.now(timezone.utc) - timedelta(days=1)
    shipping_id = shipping_service.repository.create_shipping(
        "Meest Express", ["item1"], "test-order", "created", past_date)
    
    shipping_service.process_shipping(shipping_id)
    record = shipping_service.repository.get_shipping(shipping_id)
    assert record["shipping_status"] == "failed"

def test_auto_shipping_status_update(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    past_date = datetime.now(timezone.utc) - timedelta(seconds=1)
    shipping_id = shipping_service.repository.create_shipping(
        "Нова Пошта", ["item1"], "test-order", "created", past_date
    )
    
    shipping_service.process_shipping(shipping_id)
    assert shipping_service.check_status(shipping_id) == "failed"

def test_message_sent_to_sqs_on_shipping_creation(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()
    cart.add_product(Product("Годинник", 5000, 1), 1)
    
    order = Order(cart, shipping_service)
    shipping_id = order.place_order("Нова Пошта")
    
    messages = shipping_service.publisher.poll_shipping()
    assert shipping_id in messages

def test_process_shipping_batch_from_sqs(dynamo_resource):
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    
    for _ in range(3):
        shipping_id = shipping_service.repository.create_shipping(
            "Укр Пошта", ["item1"], str(uuid.uuid4()), "created", future_date)
        shipping_service.publisher.send_new_shipping(shipping_id)

    results = shipping_service.process_shipping_batch()
    assert len(results) == 3
    for result in results:
        assert isinstance(result, dict)  