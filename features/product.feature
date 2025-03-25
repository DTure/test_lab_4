Feature: Product availability
  We want to test that product availability functionality works correctly 
  Scenario: Product is available in requested amount
    Given The product with name Product1 has availability of 10
    When I check if product is available in amount 5
    Then Product is available

  Scenario: Product is not available in requested amount
    Given The product with name Product1 has availability of 10
    When I check if product is available in amount 15
    Then Product is not available

  Scenario: Creating product with negative available amount
    Given The product with name Product2 has availability of -5
    When I check if product is available in amount 1
    Then Product is not available

  Scenario: Checking availability with None type
    Given The product with name Product3 has availability of 10
    When I check if product is available in amount None
    Then Product is not available
