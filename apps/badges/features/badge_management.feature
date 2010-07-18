Feature: Basic management of badges
    As a nice person with badge ideas
    I want to be able to manage badges
    In order to allow myself and others to reward interesting behavior

    Background:
        Given a user named "user1"
        And a user named "user2"
        And a user named "user3"
        And the "create badge" page is at "/badges/create"
        And the "browse badges" page is at "/badges/"

    Scenario: Create a new badge
        Given I am logged in as "user1"
        When I go to the "create badge" page
        And I fill in "Title" with "Awesome Tester"
        And I fill in "Description" with "This is an awesome badge for awesome testers"
        And I press "Create"
        Then I should see no form validation errors
        And I should see a page whose title contains "Badge details"
        And I should see "Awesome Tester" somewhere on the page
        When I go to the "browse badges" page
        Then I should see "Awesome Tester" somewhere on the page

    Scenario: Modify an existing badge
        Given not implemented

    Scenario: Destroy an existing badge
        Given not implemented
