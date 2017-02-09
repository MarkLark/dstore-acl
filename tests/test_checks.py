from nose.tools import eq_
from . import BaseTest, Car, Model, var, mod


class Check_ACL( BaseTest ):
    auto_add_users = True

    def test_add( self ):
        rtn = Car.acl( "add", "admin", False )
        eq_( rtn, True, "Admin should be allowed to add a Car" )

        rtn = Car.acl( "add", "member", False )
        eq_( rtn, True, "Member should be allowed to add a Car" )

        rtn = Car.acl( "add", "guest", False )
        eq_( rtn, False, "Guest should not be allowed to add a Car" )

    def test_read( self ):
        rtn = Car.acl( "read", "admin", False )
        eq_( rtn, True, "Admin should be allowed to read from Cars" )

        rtn = Car.acl( "read", "member", False )
        eq_( rtn, True, "Member should be allowed to read from Cars" )

        rtn = Car.acl( "read", "guest", False )
        eq_( rtn, True, "Guest should be allowed to read from Cars" )

    def test_update( self ):
        rtn = Car.acl( "update", "admin", False )
        eq_( rtn, True, "Admin should be allowed to update a Car" )

        rtn = Car.acl( "update", "member", False )
        eq_( rtn, False, "Member should not be allowed to update a Car" )

        rtn = Car.acl( "update", "guest", False )
        eq_( rtn, False, "Guest should not be allowed to update a Car" )

    def test_delete( self ):
        rtn = Car.acl( "delete", "admin", False )
        eq_( rtn, True, "Admin should be allowed to delete a Car" )

        rtn = Car.acl( "delete", "member", False )
        eq_( rtn, False, "Member should not be allowed to delete a Car" )

        rtn = Car.acl( "delete", "guest", False )
        eq_( rtn, False, "Guest should not be allowed to delete a Car" )
