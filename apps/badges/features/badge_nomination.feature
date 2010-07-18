Feature: Nominating users to be awarded badges
    As a nice person
    I want to be able to nominate people to be awarded badges
    In order to reward interesting behavior

    Background:
        Given a user named "user1"
            And a user named "user2"
            And a user named "user3"
            And there are no existing badges
            And the "create badge" page is at "/badges/create"
            And the "browse badges" page is at "/badges/"

    Scenario: A user nominates a user to be awarded a badge
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

    Scenario: A user nominates someone who has not signed up to the site
        Given "user1" creates a badge entitled "More awesome badge"
            And I am logged in as "user2"
            And I go to the "badge detail" page for "More awesome badge"
        When I fill in "Nominee" with "somebody@example.com"
            And I fill in "Reason why" with "somebody@example.com is awesome"
            And I press "Nominate for badge"
        Then I should see no form validation errors
            And I should see "somebody@example.com nominated" somewhere on the page
            And "somebody@example.com" should be nominated by "user2" for badge "More awesome badge" because "somebody@example.com is awesome"
            And "user1" should receive a "Badge Nomination Proposed" notification
            And "user2" should receive a "Badge Nomination Sent" notification
            And "somebody@example.com" should be sent a "Badge Nomination Received" email

    Scenario: Someone is nominated for a badge set to auto-approve
        Given "user1" creates a badge entitled "Ultimate badge"
            And the badge "Ultimate badge" has "autoapprove" set to "True"
            And I am logged in as "user2"
            And I go to the "badge detail" page for "Ultimate badge"
        When I fill in "Nominee" with "user3"
            And I fill in "Reason why" with "user3 is awesome"
            And I press "Nominate for badge"
        Then I should see no form validation errors
            And I should see "user3" somewhere in the "Awarded to" section
            And "user3" should be nominated by "user2" for badge "Ultimate badge" because "user3 is awesome"
            And "user3" should be awarded the badge "Ultimate badge"
            And "user3" should receive a "Badge Awarded" notification

