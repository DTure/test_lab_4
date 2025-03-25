Feature: Shopping cart
  We want to test that shopping cart functionality works correctly
  Scenario: Successful add product to cart
    Given The product has availability of 123
    And An empty shopping cart
    When I add product to the cart in amount 123
    Then Product is added to the cart successfully

  Scenario: Failed add product to cart
    Given The product has availability of 123
    And An empty shopping cart
    When I add product to the cart in amount 124
    Then Product is not added to cart successfully
  
  Scenario: Calculating total price of the cart with product
    Given The product has availability of 10
    And An empty shopping cart
    When I add product to the cart in amount 5
    Then The total price should be calculated correctly

  Scenario: Removing product from cart
    Given The product has availability of 5
    And An empty shopping cart
    When I add product to the cart in amount 3
    And I remove product from the cart
    Then The cart should be empty

  Scenario: Adding product with invalid type
    Given The product has availability of 5
    And An empty shopping cart
    When I add invalid amount to the cart
    Then Product is not added to cart successfully