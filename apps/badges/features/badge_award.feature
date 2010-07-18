Feature: Awarding badges
    As a nice person
    I want to be able to award badges
    In order to reward interesting behavior

    Background:
        Given a user named "user1"
        And a user named "user2"
        And a user named "user3"
        And the "create badge" page is at "/badges/create"
        And the "browse badges" page is at "/badges/"
        
    Scenario: Badge creator approves a nomination to award a badge
        Given "user1" creates a badge entitled "Nifty badge"
        And "user2" nominates "user3" for a badge entitled "Nifty badge" because "user3 is Nifty"
        And I am logged in as "user1"
        And I go to the "badge detail" page for "Nifty badge"
        When I click on "user3" in the "Nominations" section
        Then I should see a page whose title contains "Badge nomination"
        When I press "Approve"
        Then I should see a page whose title contains "Badge detail"
        And I should see "user3" somewhere in the "Awarded to" section
        And I should not see "user3" anywhere in the "Nominations" section
        And "user3" should be awarded the badge "Nifty badge"
        And "user3" should receive a "Badge Awarded" notification

    Scenario: Badge awardee accepts an award
        Given not implemented

    Scenario: Badge awardee rejects an award
        Given not implemented

    Scenario: Badge awardee has chosen to auto-accept awards
        Given not implemented

