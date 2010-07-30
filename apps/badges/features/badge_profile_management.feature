Feature: Managing badge awards on a user profile
    As a someone who's been awarded badges
    I want to be able to manage what I accept and show
    In order to control what is disclosed about me

    Background:
        Given a user named "user1"
            And a user named "user2"
            And a user named "user3"
            And a user named "user4"
            And a user named "user5"
            And a user named "user6"
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
        Then I should see a page whose title contains "Badge detail"
            And I should see "badge award claimed" somewhere on the page
            And I should see "user3" somewhere in the "claimed_by" section
            And "user1" should receive a "Badge Award Claimed" notification
            And "user2" should receive a "Badge Award Claimed" notification
            And "user3" should receive a "Badge Award Claimed" notification

    Scenario: Badge awardee accepts an award from the award page
        Given "user1" creates a badge entitled "Nifty badge"
            And "user2" nominates "user3" for a badge entitled "Nifty badge" because "user3 is Nifty"
            And "user1" approves the nomination of "user3" for a badge entitled "Nifty badge" because "user3 is indeed Nifty"
            And I am logged in as "user3"
            And I go to the "badge detail" page for "Nifty badge"
        Then I should not see the "claimed_by" section
        When I click on "user3 is Nifty" in the "claim_badge" section
        Then I should see a page whose title contains "Award details"
        When I press "action_claim_award"
        Then I should see a page whose title contains "Award details"
            And I should see "badge award claimed" somewhere on the page
            And "user1" should receive a "Badge Award Claimed" notification
            And "user2" should receive a "Badge Award Claimed" notification
            And "user3" should receive a "Badge Award Claimed" notification

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

    Scenario: An awardee can claim multiple awards of a non-unique badge
        Given "user1" creates a badge entitled "Nifty badge"
            And "user2" nominates "user3" for a badge entitled "Nifty badge" because "user3 is nifty"
            And "user4" nominates "user3" for a badge entitled "Nifty badge" because "nifty is user3"
            And "user5" nominates "user3" for a badge entitled "Nifty badge" because "nifty nifty nifty"
            And "user1" approves "user2"'s nomination of "user3" for a badge entitled "Nifty badge" because "yes"
            And "user1" approves "user4"'s nomination of "user3" for a badge entitled "Nifty badge" because "okay"
            And "user1" approves "user5"'s nomination of "user3" for a badge entitled "Nifty badge" because "sure"
            And I am logged in as "user3"
            And I go to the "badge detail" page for "Nifty badge"
        Then "user3" should have "3" unclaimed awards for the badge "Nifty badge"
            And I should see "user2" somewhere in the "pending_awards" section
            And I should see "user3 is nifty" somewhere in the "pending_awards" section
            And I should see "user4" somewhere in the "pending_awards" section
            And I should see "nifty is user3" somewhere in the "pending_awards" section
            And I should see "user5" somewhere in the "pending_awards" section
            And I should see "nifty nifty nifty" somewhere in the "pending_awards" section
        When I find the form containing "user3 is nifty" in the "claim_badge" section
            And I press "action_claim_award"
        Then I should see a page whose title contains "Badge detail"
            And "user3" should have "1" claimed awards for the badge "Nifty badge"
            And "user3" should have "2" unclaimed awards for the badge "Nifty badge"
        When I find the form containing "nifty is user3" in the "claim_badge" section
            And I press "action_claim_award"
        Then "user3" should have "2" claimed awards for the badge "Nifty badge"
            And "user3" should have "1" unclaimed awards for the badge "Nifty badge"
        When I find the form containing "nifty nifty nifty" in the "claim_badge" section
            And I press "action_claim_award"
        Then "user3" should have "3" claimed awards for the badge "Nifty badge"
            And "user3" should have "0" unclaimed awards for the badge "Nifty badge"

    @current
    Scenario: Display of multiple awards on a profile page is collapsed into a single image with a counter
        # But clicking on one of them should yield a report of awards and nominations
        # ANOTHER SCENARIO LEFT UNDONE WHILE FEATURE SEEMS TO WORK UGH
        Given in progress

    @current
    Scenario: Display of multiple awards on a badge detail page is collapsed into a single image with a counter
        # But clicking on one of them should yield a report of awards and nominations
        # ANOTHER SCENARIO LEFT UNDONE WHILE FEATURE SEEMS TO WORK UGH
        Given in progress

    @TODO
    Scenario: Someone confirms an email address for which badges have been awarded
        # Retroactive claim of BadgeAwardee objects without associated users
        Given in progress

    @TODO
    Scenario: Badge awardee has chosen to auto-accept awards
        # This should be a profile setting.
        Given in progress

    @TODO
    Scenario: Badge awardee chooses to auto-accept awards in the future
        # Claim form for an award should have a checkbox that says something
        # like "Accept future awards automatically?" Should it be per badge?
        Given in progress

    @TODO
    Scenario: User wants to claim a previously ignored badge award
        # Rejection deletes the award, but ignore just hides it
        # Provide a way to undo the ignore decision?
        # A link in "award ignored" notification leads back to the hidden award
        Given in progress

    @TODO
    Scenario: Badge awardee decides to hide an award after accepting it
        # Makes an awarded badge invisible to public
        # Move to a "hidden badges" collection, so user doesn't have to see it
        # anymore, but can un-hide in the future
        Given in progress

    @TODO
    Scenario: Badge awardee decides to reveal an award after hiding it
        Given in progress
