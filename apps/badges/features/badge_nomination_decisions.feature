Feature: Making decisions about badge award nominations
    As a badge creator (and nice person)
    I want to be able to make decisions on award nominations
    In order to reward interesting behavior

    Background:
        Given a user named "user1"
            And a user named "user2"
            And a user named "user3"
            And a user named "user4"
            And there are no existing badges
            And the "create badge" page is at "/badges/create"
            And the "browse badges" page is at "/badges/"
        
    @FIXME
    Scenario: Badge creator approves a nomination to award a badge
        Given "user1" creates a badge entitled "Nifty badge"
        And "user2" nominates "user3" for a badge entitled "Nifty badge" because "user3 is Nifty"
        And I am logged in as "user1"
        And I go to the "badge detail" page for "Nifty badge"
        When I click on "nomination_details" in the "nominations" section
        Then I should see a page whose title contains "Nomination details"
        When I press "Approve"
        Then I should see a page whose title contains "Nomination details"
        And I should see "approved this nomination" somewhere on the page
        And "user3" should be awarded the badge "Nifty badge"
        And "user3" should receive a "Badge Award Received" notification
        Given I am logged in as "user3"
        And I go to the "badge detail" page for "Nifty badge"
        Then I should see the "claim_badge" section

    @FIXME
    Scenario: User must be badge creator to approve a nomination
        Given "user1" creates a badge entitled "Nifty badge"
            And "user2" nominates "user3" for a badge entitled "Nifty badge" because "user3 is Nifty"
            And I am logged in as "user1"
        When I go to the "badge detail" page for "Nifty badge"
            And I click on "user3 is Nifty" in the "nominations" section
        Then I should see a page whose title contains "Nomination details"
        Given I am logged in as "user3"
        When I press "Approve"
        Then I should see a status code of "403"

    @FIXME
    Scenario: Badge creator rejects a nomination to award a badge
        Given "user1" creates a badge entitled "Nifty badge"
            And "user2" nominates "user3" for a badge entitled "Nifty badge" because "user3 is Nifty"
            And I am logged in as "user1"
            And I go to the "badge detail" page for "Nifty badge"
        When I click on "user3 is Nifty" in the "nominations" section
        Then I should see a page whose title contains "Nomination details"
        When I fill in "Reason why" with "Your niftiness is lacking"
            And I press "Reject"
        Then I should see a page whose title contains "Badge detail"
            And I should not see the "awarded_to" section
            And I should not see the "nominations" section
            And "user1" should receive a "Badge Nomination Rejected" notification
            And "user2" should receive a "Badge Nomination Rejected" notification

    @FIXME
    Scenario: Badge nomination rejection should require a reason
        Given "user1" creates a badge entitled "Nifty badge"
            And "user2" nominates "user3" for a badge entitled "Nifty badge" because "user3 is Nifty"
            And I am logged in as "user1"
            And I go to the "badge detail" page for "Nifty badge"
        When I click on "user3 is Nifty" in the "nominations" section
        Then I should see a page whose title contains "Nomination details"
        When I press "Reject"
        Then I should see form validation errors

    @FIXME
    Scenario: A badge nominator can reject own nomination
        Given "user1" creates a badge entitled "Nifty badge"
            And "user2" nominates "user3" for a badge entitled "Nifty badge" because "user3 is Nifty"
            And I am logged in as "user1"
        When I go to the "badge detail" page for "Nifty badge"
            And I click on "user3 is Nifty" in the "nominations" section
        Then I should see a page whose title contains "Nomination details"
        Given I am logged in as "user2"
        When I press "Reject"
        Then I should see a status code of "200"

    @FIXME
    Scenario: A badge nominee can reject own nomination
        Given "user1" creates a badge entitled "Nifty badge"
            And "user2" nominates "user3" for a badge entitled "Nifty badge" because "user3 is Nifty"
            And I am logged in as "user1"
        When I go to the "badge detail" page for "Nifty badge"
            And I click on "user3 is Nifty" in the "nominations" section
        Then I should see a page whose title contains "Nomination details"
        Given I am logged in as "user3"
        When I press "Reject"
        Then I should see a status code of "200"

