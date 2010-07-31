Feature: Display details on a badge
    As someone who is curious about a badge
    I want to be able to view details about the badge
    In order to know more about the badge

    Background:
        Given a user named "user1"
            And a user named "user2"
            And a user named "user3"
            And there are no existing badges

    Scenario: Display of multiple awards is collapsed into a single image with a counter
        Given "user1" creates a badge entitled "Nifty badge"
            And "user2" nominates "user3" for a badge entitled "Nifty badge" because "user3 is Nifty #1"
            And "user1" approves the nomination of "user3" for a badge entitled "Nifty badge" because "user3 is indeed Nifty #1"
            And "user3" claims the award nominated by "user2" for a badge entitled "Nifty badge"
            And "user2" nominates "user3" for a badge entitled "Nifty badge" because "user3 is Nifty #2"
            And "user1" approves the nomination of "user3" for a badge entitled "Nifty badge" because "user3 is indeed Nifty #2"
            And "user3" claims the award nominated by "user2" for a badge entitled "Nifty badge"
            And "user2" nominates "user3" for a badge entitled "Nifty badge" because "user3 is Nifty #3"
            And "user1" approves the nomination of "user3" for a badge entitled "Nifty badge" because "user3 is indeed Nifty #3"
            And "user3" claims the award nominated by "user2" for a badge entitled "Nifty badge"
        When I go to the profile page for "user3" 
        Then "user3" should have "3" awards for the badge "Nifty badge"
            And I should see "Nifty badge" somewhere in the "awarded_badges" section
            And I should see "3" somewhere in the "awarded_badges" section
        When I go to the "badge detail" page for "Nifty badge"
        Then I should see "user3" somewhere in the "claimed_by" section
            And I should see "3" somewhere in the "claimed_by" section
        Given "user2" nominates "user3" for a badge entitled "Nifty badge" because "user3 is Nifty #4"
            And "user1" approves the nomination of "user3" for a badge entitled "Nifty badge" because "user3 is indeed Nifty #4"
            And "user3" claims the award nominated by "user2" for a badge entitled "Nifty badge"
        When I go to the profile page for "user3" 
        Then "user3" should have "4" awards for the badge "Nifty badge"
            And I should see "Nifty badge" somewhere in the "awarded_badges" section
            And I should see "4" somewhere in the "awarded_badges" section
        When I go to the "badge detail" page for "Nifty badge"
        Then I should see "user3" somewhere in the "claimed_by" section
            And I should see "4" somewhere in the "claimed_by" section
        Given "user2" nominates "user3" for a badge entitled "Nifty badge" because "user3 is Nifty #5"
            And "user1" approves the nomination of "user3" for a badge entitled "Nifty badge" because "user3 is indeed Nifty #5"
            And "user3" claims the award nominated by "user2" for a badge entitled "Nifty badge"
        When I go to the profile page for "user3" 
        Then "user3" should have "5" awards for the badge "Nifty badge"
            And I should see "Nifty badge" somewhere in the "awarded_badges" section
            And I should see "5" somewhere in the "awarded_badges" section
        When I go to the "badge detail" page for "Nifty badge"
        Then I should see "user3" somewhere in the "claimed_by" section
            And I should see "5" somewhere in the "claimed_by" section
