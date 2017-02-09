from nose.tools import raises
from . import BaseTest, Car, Model, var, mod
from dstore_acl import Rule, Role, Action, AccessDenied, ActionNotFound


class Car_ACL( BaseTest ):
    auto_add_users = True

    def test_action_not_found( self ):
        with assert_raises( ActionNotFound ):
            Car.acl.something_new

    def test_add( self ):
        self.user = "admin"
        Car( manufacturer = "Holden", make = "Commodore", year = 2005 ).add()

        self.user = "member"
        Car( manufacturer = "Holden", make = "Commodore", year = 2006 ).add()

        self.user = "guest"
        with assert_raises( AccessDenied ):
            Car( manufacturer = "Holden", make = "Commodore", year = 2005 ).add()

    def test_model_update( self ):
        self.user = "admin"
        car = Car( manufacturer = "Holden", make = "Commodore", year = 2005 ).add()

        car.year = 2006
        car.update()

        self.user = "member"
        car.year = 2007
        with assert_raises( AccessDenied ):
            car.update()

        self.user = "guest"
        car.year = 2008
        with assert_raises( AccessDenied ):
            car.update()

    def test_model_delete( self ):
        self.user = "admin"
        car = Car( manufacturer = "Holden", make = "Commodore", year = 2005 ).add()

        self.user = "member"
        with assert_raises( AccessDenied ):
            car.delete()

        self.user = "guest"
        with assert_raises( AccessDenied ):
            car.delete()

        self.user = "admin"
        car.delete()

    def test_model_empty( self ):
        self.add_users()

        self.user = "member"
        Car( manufacturer = "Holden", make = "Commodore", year = 2005 ).add()
        Car( manufacturer = "Holden", make = "Commodore", year = 2006 ).add()
        Car( manufacturer = "Holden", make = "Commodore", year = 2007 ).add()

        with assert_raises( AccessDenied ):
            Car.empty()

        self.user = "guest"
        with assert_raises( AccessDenied ):
            Car.empty()

        self.user = "admin"
        Car.empty()

    def test_print_events( self ):
        print
        self.print_tables()

    def print_tables( self ):
        print( "\nACL.Action:" )
        Action.print_table()

        print( "\nACL.Role:" )
        Role.print_table()

        print( "\nACL.Rule:" )
        Rule.print_table()
