Feature: Basic management of badges
    As a nice person
    I want to be able to create badges
    In order to reward interesting behavior

    Background:
        Given a user named "user1"
        And a user named "user2"
        And a user named "user3"
        And the "create badge" page is at "/badges/create"
        And the "browse badges" page is at "/badges/"

    Scenario: Create a new badge
        Given I am logged in as "user1"
        And I go to the "create badge" page
        When I fill in "Title" with "Awesome Tester"
        And I fill in "Description" with "This is an awesome badge for awesome testers"
        And I press "Create"
        Then I should see no form validation errors
        And I should see a page entitled "Badge details"
        And I should see "Awesome Tester" somewhere on the page

    Scenario: Look for a badge on the browse badges page
        Given "user1" creates a badge entitled "More awesome badge"
        When I go to the "browse badges" page
        Then I should see "More awesome badge" somewhere on the page
