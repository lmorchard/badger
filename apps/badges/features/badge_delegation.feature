Feature: Delegating badge nomination management to other users
    As a nice person
    I want to be able to award badges
    In order to reward interesting behavior

    Background:
        Given a user named "user1"
            And a user named "user2"
            And a user named "user3"
            And a user named "user4"
            And there are no existing badges
            And the "create badge" page is at "/badges/create"
            And the "browse badges" page is at "/badges/"
        
    @TODO
    Scenario: Badge creator delegates approval of nomination to another user

    @TODO
    Scenario: Badge delegate rejects a nomination to award a badge

    @TODO
    Scenario: Badge delegate approves a nomination to award a badge

    @TODO
    Scenario: Badge creator revokes approval delegation for another user

    @TODO
    Scenario: Badges can be set to automatically flag all awardees as delegates

