Feature: Managing badge awards on a user profile
    As a someone who's been awarded badges
    I want to be able to manage what I accept and show
    In order to control what is disclosed about me

    Background:
        Given a user named "user1"
            And a user named "user2"
            And a user named "user3"
            And a user named "user4"
            And there are no existing badges
            And the "create badge" page is at "/badges/create"
            And the "browse badges" page is at "/badges/"
        
    Scenario: Badge awardee accepts an award
        Given "user1" creates a badge entitled "Nifty badge"
            And "user2" nominates "user3" for a badge entitled "Nifty badge" because "user3 is Nifty"
            And "user1" approves the nomination of "user3" for a badge entitled "Nifty badge" because "user3 is indeed Nifty"
            And I am logged in as "user3"
            And I go to the "badge detail" page for "Nifty badge"
        Then I should not see the "claimed_by" section
        When I press "action_claim_award"
        Then I should see a page whose title contains "Profile for"
            And I should see "badge award claimed" somewhere on the page
            And I should see "Nifty badge" somewhere in the "badge_awards" section
            And "user1" should receive a "Badge Award Claimed" notification
            And "user2" should receive a "Badge Award Claimed" notification
            And "user3" should receive a "Badge Award Claimed" notification
        Given I go to the "badge detail" page for "Nifty badge"
        Then I should see "user3" somewhere in the "claimed_by" section
            And I should not see "Claim this badge" anywhere on the page

    Scenario: Badge awardee rejects an award
        Given "user1" creates a badge entitled "Nifty badge"
            And "user2" nominates "user3" for a badge entitled "Nifty badge" because "user3 is Nifty"
            And "user1" approves the nomination of "user3" for a badge entitled "Nifty badge" because "user3 is indeed Nifty"
            And I am logged in as "user3"
            And I go to the "badge detail" page for "Nifty badge"
        Then I should not see the "claimed_by" section
        When I press "action_reject_award"
        Then I should see a page whose title contains "Badge details"
            And I should see "badge award rejected" somewhere on the page
            And "user1" should receive a "Badge Award Rejected" notification
            And "user2" should receive a "Badge Award Rejected" notification
            And "user3" should receive a "Badge Award Rejected" notification
            And "user3" should not be awarded the badge "Nifty badge"
            And "user3" should not be nominated for the badge "Nifty badge"
            And I should not see the "claimed_by" section
            And I should not see "Claim this badge" anywhere on the page
        When I go to the profile page for "user3"
        Then I should not see "Nifty badge" anywhere on the page


    Scenario: Badge awardee ignores an award
        Given "user1" creates a badge entitled "Nifty badge"
            And "user2" nominates "user3" for a badge entitled "Nifty badge" because "user3 is Nifty"
            And "user1" approves the nomination of "user3" for a badge entitled "Nifty badge" because "user3 is indeed Nifty"
            And I am logged in as "user3"
            And I go to the "badge detail" page for "Nifty badge"
        Then I should not see the "claimed_by" section
        When I press "action_ignore_award"
        Then I should see a page whose title contains "Badge details"
            And "user3" should receive a "Badge Award Ignored" notification
            And I should not see the "claimed_by" section
            And I should not see "Claim this badge" anywhere on the page
            And "user3" should be awarded the badge "Nifty badge"
            And "user3" should be nominated by "user2" for badge "Nifty badge" because "user3 is Nifty"
        When I go to the profile page for "user3"
        Then I should not see "Nifty badge" anywhere on the page

    @TODO
    Scenario: Badge awardee has chosen to auto-accept awards
        Given in progress

    @TODO
    Scenario: Badge awardee chooses to auto-accept awards in the future
        Given in progress

    @TODO
    Scenario: Badge awardee decides to hide an award after accepting it
        Given in progress

    @TODO
    Scenario: Someone confirms an email address for which badges have been awarded
        Given in progress

    @TODO
    Scenario: User wants to claim a previously ignored badge award
        # Rejection deletes the award, but ignore just hides it
        # Provide a way to undo the ignore decision?
        # A link in "award ignored" notification leads back to the hidden award
        Given in progress
