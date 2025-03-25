Feature: Order placement functionality
  We want to test that the order placement functionality works correctly
  Scenario: Successful order placement with a product
    Given A product with name "Product1" and availability of 10
    And An empty shopping cart for order
    When I add product to the shopping cart for order with amount 3
    And I place the order
    Then The shopping cart is empty after order

  Scenario: Failed order placement due to insufficient product availability
    Given A product with name "Product1" and availability of 3
    And An empty shopping cart for order
    When I add product to the shopping cart for order with amount 5
    Then The shopping cart contains the product after order

  Scenario: Order with multiple products
    Given A product with name "Product1" and availability of 10
    And A product with name "Product2" and availability of 5
    And An empty shopping cart for order
    When I add product to the shopping cart for order with amount 3
    And I add product to the shopping cart for order with amount 2
    And I place the order
    Then The shopping cart is empty after order

