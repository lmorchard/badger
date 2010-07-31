Feature: Awarding badges to email addresses
    As a nice person
    I want to be able to award a badge to an email address
    In order to reward someone who may not yet have a profile

    Background:
        Given a user named "user1"
            And a user named "user2"
            And a user named "user3"
            And there are no existing badges
        
    Scenario: An award sent to an unknown email address should result in a message sent containing a verification claim URL
        Given "user1" creates a badge entitled "Nifty badge"
            And "user2" nominates "user3@example.com" for a badge entitled "Nifty badge" because "user3 is Nifty"
            And "user1" approves the nomination of "user3@example.com" for a badge entitled "Nifty badge" because "user3 is indeed Nifty"
        Then "user3@example.com" should be sent a "Badge Award Verification" email
            And the email should contain a URL
        Given I am logged out
        When I visit the URL
        Then I should see a page whose title contains "Login"
        When I fill in "username" with "user3"
            And I fill in "password" with "user3_password"
            And I press "Log in"
        Then I should see a page whose title contains "Award details"
        When I press "action_claim_award"
        Then I should see no form validation errors
            And "user3" should be awarded the badge "Nifty badge"
            And "user3" should have "1" claimed awards for the badge "Nifty badge"
            And "user1" should receive a "badge_award_claimed" notification
            And "user2" should receive a "badge_award_claimed" notification
            And "user3" should receive a "badge_award_claimed" notification
        # The claim URL should not be reusable by another user.
        Given I am logged in as "user4"
        When I visit the URL
        Then I should see a status code of "404"
