Feature: Nominating users to be awarded badges
    As a nice person
    I want to be able to nominate people to be awarded badges
    In order to reward interesting behavior

    Background:
        Given a user named "user1"
        And a user named "user2"
        And a user named "user3"
        And the "create badge" page is at "/badges/create"
        And the "browse badges" page is at "/badges/"

    Scenario: A user nominates someone to be awarded a badge
        Given "user1" creates a badge entitled "Awesome badge"
        And I am logged in as "user2"
        And I go to the "badge detail" page for "Awesome badge"
        When I fill in "Nominee" with "user3"
        And I fill in "Reason why" with "user3 is awesome"
        And I press "Nominate for badge"
        Then I should see no form validation errors
        And I should see "user3 nominated" somewhere on the page
        And I should see "user3" somewhere in the "Nominations" section
        And "user3" should be nominated by "user2" for badge "Awesome badge" because "user3 is awesome"
        And "user1" should receive a "Badge Nomination Proposed" notification
        And "user2" should receive a "Badge Nomination Sent" notification
        And "user3" should receive a "Badge Nomination Received" notification
