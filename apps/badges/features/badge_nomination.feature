Feature: Nominating people for badges
    As a nice person
    I want to be able to nominate people to be awarded badges
    In order to reward interesting behavior

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

    Scenario: A user nominates a user to be awarded a badge
        Given "user1" creates a badge entitled "Awesome badge"
            And I am logged in as "user2"
            And I go to the "badge detail" page for "Awesome badge"
        When I fill in "Nominee" with "user3"
            And I fill in "Reason why" with "user3 is awesome"
            And I press "Nominate for badge"
        Then I should see no form validation errors
            And I should see "user3 nominated" somewhere on the page
            And "user3" should be nominated by "user2" for badge "Awesome badge" because "user3 is awesome"
            And "user1" should receive a "Badge Nomination Proposed" notification
            And "user2" should receive a "Badge Nomination Sent" notification
        Given I am logged in as "user1"
            And I go to the "badge detail" page for "Awesome badge"
        Then I should see "user3" somewhere in the "nominations" section

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

    @TODO
    Scenario: A nominations from a badge creator is auto-approved
        Given in progress

    Scenario: Someone is nominated for a badge set to auto-approve for everyone
        Given "user1" creates a badge entitled "Ultimate badge"
            And the badge "Ultimate badge" has "autoapprove" set to "True"
            And I am logged in as "user2"
            And I go to the "badge detail" page for "Ultimate badge"
        When I fill in "Nominee" with "user3"
            And I fill in "Reason why" with "user3 is awesome"
            And I press "Nominate for badge"
        Then I should see no form validation errors
            And "user3" should be nominated by "user2" for badge "Ultimate badge" because "user3 is awesome"
            And "user3" should be awarded the badge "Ultimate badge"
            And "user3" should receive a "Badge Awarded" notification
        Given I am logged in as "user3"
            And I go to the "badge detail" page for "Ultimate badge"
        Then I should see the "claim_badge" section

    Scenario: Nomination should not display nomination form, once approved
        Given "user1" creates a badge entitled "Nifty badge"
            And "user2" nominates "user3" for a badge entitled "Nifty badge" because "user3 is nominated for nifty"
            And I am logged in as "user1"
            And I go to the "badge detail" page for "Nifty badge"
        When I click on "user3 is nominated for nifty" in the "nominations" section
        Then I should see a page whose title contains "Badge nomination"
        When I press "Approve"
        Then I should see a page whose title contains "Badge nomination"
        When I go to the "badge detail" page for "Nifty badge"
        Then I should not see the "nominations" section
            And "user3" should be awarded the badge "Nifty badge"
            And "user3" should receive a "Badge Awarded" notification
        When I click on "Inbox" in the "login" section
            And I click on "user3 is nominated for nifty" in the "Notices" section
        Then I should see a page whose title contains "Badge nomination"
            And I should not see "Reason why" anywhere on the page
            And I should not see "Reject" anywhere on the page

    Scenario: Multiple separate nominations can be submitted for a non-unique badge
        # There should only be one nomination per nominator + nominee + badge
        # at a given time. But, multiple individual nominators can submit
        # their own nominations, each of which can be approved and claimed 
        # as multiple awards. (Claiming them is covered in another feature.)
        Given "user1" creates a badge entitled "Nifty badge"
            And "user2" nominates "user3" for a badge entitled "Nifty badge" because "user3 is nominated for nifty"
            And I am logged in as "user2"
            And I go to the "badge detail" page for "Nifty badge"
        When I fill in "Nominee" with "user3"
            And I fill in "Reason why" with "user3 is still awesome"
            And I press "Nominate for badge"
        Then I should see form validation errors
        Given I am logged in as "user4"
            And I go to the "badge detail" page for "Nifty badge"
        When I fill in "Nominee" with "user3"
            And I fill in "Reason why" with "I think user3 is awesome for another thing"
            And I press "Nominate for badge"
        Then I should see no form validation errors
        Given "user1" approves "user2"'s nomination of "user3" for a badge entitled "Nifty badge" because "user3 is indeed Nifty"
            And I am logged in as "user2"
        When I fill in "Nominee" with "user3"
            And I fill in "Reason why" with "user3 has shown awesomeness yet again"
            And I press "Nominate for badge"
        Then I should see no form validation errors
        Given I am logged in as "user4"
            And I go to the "badge detail" page for "Nifty badge"
        When I fill in "Nominee" with "user3"
            And I fill in "Reason why" with "I think user3 continues to be awesome for another thing"
            And I press "Nominate for badge"
        Then I should see form validation errors
        Given "user1" approves "user4"'s nomination of "user3" for a badge entitled "Nifty badge" because "I know, I know"
            And I am logged in as "user4"
            And I go to the "badge detail" page for "Nifty badge"
        When I fill in "Nominee" with "user3"
            And I fill in "Reason why" with "I think user3 continues to be awesome for another thing"
            And I press "Nominate for badge"
        Then I should see no form validation errors

    @TODO
    Scenario: A subsequent nomination for a unique badge is a second
        # Multiple nominations should be allowed for a unique badge, but as "seconded"
        Given in progress
        Given "user1" creates a badge entitled "Ultimate badge"
            And I am logged in as "user2"
            And I go to the "badge detail" page for "Ultimate badge"
        When I fill in "Nominee" with "user3"
            And I fill in "Reason why" with "user3 is awesome"
            And I press "Nominate for badge"
        Then I should see no form validation errors
        Given I am logged in as "user1"
        When I go to the "badge detail" page for "Ultimate badge"
        Then I should see "user3" somewhere in the "nominations" section
        Given I am logged in as "user2"
        When I go to the "badge detail" page for "Ultimate badge"
            And I fill in "Nominee" with "user3"
            And I fill in "Reason why" with "user3 is awesome"
            And I press "Nominate for badge"
        Then I should see form validation errors

    Scenario: User must be badge creator to see nominations listed
        Given "user1" creates a badge entitled "Nifty badge"
            And "user2" nominates "user3" for a badge entitled "Nifty badge" because "user3 is Nifty"
        Given I am logged in as "user2"
        When I go to the "badge detail" page for "Nifty badge"
        Then I should not see the "nominations" section
        Given I am logged in as "user3"
        When I go to the "badge detail" page for "Nifty badge"
        Then I should not see the "nominations" section
        Given I am logged in as "user4"
        When I go to the "badge detail" page for "Nifty badge"
        Then I should not see the "nominations" section
        Given I am logged in as "user1"
        When I go to the "badge detail" page for "Nifty badge"
        Then I should see "user3" somewhere in the "nominations" section

    Scenario: User can be a nominator or nominee to see related nomination
        Given "user1" creates a badge entitled "Nifty badge"
            And "user2" nominates "user3" for a badge entitled "Nifty badge" because "user3 is Nifty"
            And I am logged in as "user4"
        When I go to the "badge detail" page for "Nifty badge"
        Then I should not see the "nominations" section
        Given I am logged in as "user1"
        When I go to the "badge detail" page for "Nifty badge"
        Then I should see "user3" somewhere in the "nominations" section
        Given I am logged in as "user3"
        When I click on "user3 is Nifty" in the "nominations" section
        Then I should see a status code of "200"
            And I should see a page whose title contains "Badge nomination"
        Given I am logged in as "user2"
        When I reload the page
        Then I should see a status code of "200"
            And I should see a page whose title contains "Badge nomination"

    @TODO
    Scenario: Badges can be set to deny self-nomination
        # So that a 3rd party or creator must nominate
        Given in progress

    @TODO
    Scenario: Badges can be set as a surprise, so nominee gets no notifications
        # Only the creator and nominator are involved
        # That way, the nominee is surprised by the ultimate award
        Given in progress

    @TODO
    Scenario: Badges can be assigned a secret claim code for auto-nomination
        Given in progress
        # Code should be short and easy for mobile typing
        # Say 6 letters and numbers: 36 ** 6 == 2176782336
        # To be written on a whiteboard at an event
        # To be encoded as a QR code on a patch/sticker
        # Only the badge creator can see the code
