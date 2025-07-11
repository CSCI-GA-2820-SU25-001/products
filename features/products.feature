Feature: The product store service back-end
    As a Store Owner
    I need a RESTful catalog service
    So that I can keep track of all my products

Background:
    Given the following products
        | name        | description                          | available    | price   |
        | toothbrush  | it's a brush for your teeth          | True         | 5.43    | 
        | laptop      | it's a laptop                        | True         | 253.72  | 
        | gum         | it's 1 pack of gum                   | False        | 1.99    | 
        | shampoo     | its a bottle of shampoo              | True         | 15.49   | 

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Product REST API Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Product
    When I visit the "Home Page"
    And I set the "Name" to "toothbrush"
    And I set the "Description" to "it's a brush for your teeth"
    And I select "False" in the "Available" dropdown
    And I set the "Price" to "5.43"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Description" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "toothbrush" in the "Name" field
    And I should see "it's a brush for your teeth" in the "Description" field
    And I should see "False" in the "Available" dropdown
    And I should see "5.43" in the "Price" field

Scenario: List all products
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "toothbrush" in the results
    And I should see "laptop" in the results
    And I should see "gum" in the results
    And I should see "shampoo" in the results

Scenario: Search for description
    When I visit the "Home Page"
    And I set the "Description" to "it's a brush for your teeth"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "toothbrush" in the results

Scenario: Search for available
    When I visit the "Home Page"
    And I select "True" in the "Available" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "toothbrush" in the results
    And I should see "laptop" in the results
    And I should see "shampoo" in the results

Scenario: Update a Product
    When I visit the "Home Page"
    And I set the "Name" to "toothbrush"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "toothbrush" in the "Name" field
    And I should see "it's a brush for your teeth" in the "Description" field
    When I change "Name" to "Colgate Brush"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Colgate Brush" in the "Name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Colgate Brush" in the results
    And I should not see "toothbrush" in the results

Scenario: Purchase a product
    When I visit the "Home Page"
    And I set the "Name" to "toothbrush"
    And I press the "Search" button
    When I purchase the product named "toothbrush"
    Then I should see the message "Success"
    And I should see "toothbrush" in the "Name" field

Scenario: Search for products by name
    When I visit the "Home Page"
    And I set the "Name" to "toothbrush"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "toothbrush" in the results
    And I should not see "laptop" in the results

Scenario: Search for products by price
    When I visit the "Home Page"
    And I set the "Price" to "5.43"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "toothbrush" in the results
    And I should not see "laptop" in the results