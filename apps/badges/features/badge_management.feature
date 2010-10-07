Feature: Badge creation and management
    As a nice person with badge ideas
    I want to be able to manage badges
    In order to allow myself and others to reward interesting behavior

    Background:
        Given a user named "user1"
            And a user named "user2"
            And a user named "user3"
            And there are no existing badges
            And the "create badge" page is at "/badges/create"
            And the "browse badges" page is at "/badges/all/"

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

    @TODO
    Scenario: A badge is flagged as unlisted and hidden from search
        # For surprises, hidden achievements

    Scenario: Modify an existing badge
        Given "user1" creates a badge entitled "Nifty badge"
            And I am logged in as "user1"
            And I go to the "badge detail" page for "Nifty badge"
        When I click on "edit_badge" in the "badge" section
        Then I should see a page whose title contains "Badge edit"
        When I fill in "Title" with "More Nifty Badge"
            And I fill in "Description" with "Some description"
            And I press "Save"
        Then I should see a page whose title contains "Badge details"
            And I should see "More Nifty Badge" somewhere in the "badge" section
            And there should be no badge "Nifty badge"

    @TODO
    Scenario: Awardees should be notified when a badge has been modified
        # If a badge is modified, awardees should be notified, in case they no
        # longer like the badge. Or, in case it's gotten more awesome.
        Given in progress

    @TODO
    Scenario: Destroy an existing badge, before any awards have been approved
        # Only allow for non-admins if no nominations or awards have been issued?
        Given in progress

    @TODO
    Scenario: A badge cannot be delete after it has been awarded
        Given in progress

    @TODO
    Scenario: Badges should accept image uploads
        Given I am logged in as "user1"
        When I go to the "create badge" page
            And I fill in "Title" with "Awesome Tester"
            And I fill in "Description" with "This is an awesome badge for awesome testers"
            And I fill in "Main image" with "garbage"
            # Ugh. Stumped here on how best to actually test an image upload.
            # This only checks for the presence of the field.
