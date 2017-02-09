from nose.tools import eq_, raises
from . import BaseTest, Car, Model, var, mod, UserProfile, UserAccount
from dstore_acl import Rule, Role, Action, AccessDenied


class Profile_ACL( BaseTest ):
    models = [ Car, UserAccount, UserProfile ]
    auto_add_users = True

    def test_add_own( self ):
        user = self.get_user( "admin" )
        UserProfile( nickname = "Miny", users_account_id = user.id ).add()

    def test_add_others( self ):
        # Admin can add a profile for Member
        user = self.get_user( "member" )
        self.user = "admin"
        UserProfile( nickname = "Miny", users_account_id = user.id ).add()

        # Member cannot add a profile for Admin
        user = self.get_user("admin")
        self.user = "member"
        self.assertRaises( AccessDenied, UserProfile( nickname = "Membrain", users_account_id = user.id ).add )

    def test_update_own( self ):
        user = self.get_user( "admin" )
        UserProfile( nickname = "Miny", users_account_id = user.id ).add()

        profile = UserProfile.filter( users_account_id = user.id )[0]
        profile.nickname = "Addy"
        profile.update()

    def test_update_others( self ):
        admin = self.get_user( "admin" )
        admin_prof = UserProfile( nickname = "Miny", users_account_id = admin.id ).add()

        member = self.get_user( "member" )
        member_prof = UserProfile( nickname = "Membrain", users_account_id = member.id ).add()

        # Admin can update Member profile
        self.user = "admin"
        member_prof.nickname = "Mobrain"
        member_prof.update()

        # Member cannot update Admin profile
        self.user = "member"
        admin_prof.nickname = "Aiden"
        self.assertRaises( AccessDenied, admin_prof.update )

    def test_delete_own( self ):
        guest = self.get_user( "guest" )
        UserProfile( nickname = "Gussy", users_account_id = guest.id ).add()

        member = self.get_user( "member" )
        UserProfile( nickname = "Membrain", users_account_id = member.id ).add()

        # Member should be able to delete their own Profile
        UserProfile.filter( users_account_id = member.id )[0].delete()

    def test_delete_others( self ):
        admin = self.get_user( "admin" )
        admin_prof = UserProfile( nickname = "Miny", users_account_id = admin.id ).add()

        member = self.get_user( "member" )
        member_prof = UserProfile( nickname = "Membrain", users_account_id = member.id ).add()

        # Admin can delete Member profile
        self.user = "admin"
        member_prof.delete()

        # Member cannot delete Admin profile
        self.user = "member"
        self.assertRaises( AccessDenied, admin_prof.delete )

    def test_get_own( self ):
        member = self.get_user( "member" )
        profile = UserProfile( nickname = "Membrain", users_account_id = member.id ).add()

        UserProfile.get( profile.id )

    def test_get_other( self ):
        member = self.get_user( "member" )
        profile = UserProfile( nickname = "Membrain", users_account_id = member.id ).add()

        self.get_user("guest")
        self.assertRaises( AccessDenied, UserProfile.get, profile.id )

        self.get_user( "admin" )
        UserProfile.get( profile.id )

    def test_all_auto_filter( self ):
        guest = self.get_user( "guest" )
        UserProfile( nickname = "Gussy", users_account_id = guest.id ).add()

        member = self.get_user( "member" )
        UserProfile( nickname = "Membrain", users_account_id = member.id ).add()

        admin = self.get_user( "admin" )
        UserProfile( nickname = "Addy", users_account_id = admin.id ).add()

        print( "\n\nGUEST" )
        self.get_user( "guest" )
        profiles = UserProfile.all()

        print( "\n\nGuest profiles:" )
        for p in profiles: print( p )

        num_profiles = len( profiles )
        eq_( num_profiles, 1, "Guest should only be able to get 1 profile, not %d" % num_profiles )

        print( "\n\nADMIN" )
        for p in self.store.data[ "users.profile" ]: print( p )

        self.get_user( "admin" )
        profiles = UserProfile.all()

        print( "\n\nAdmin Profiles:" )
        for p in profiles: print( p )
        print( "\n\n" )

        num_profiles = len( profiles )
        eq_( num_profiles, 3, "Admin should only be able to get 3 profiles, not %d" % num_profiles )

    def test_read_own_deny( self ):
        member = self.get_user( "member" )
        UserProfile( nickname = "Membrain", users_account_id = member.id ).add()

        action = Action.filter( model = "users.profile", name = "read_own" )[0]
        role   = Role.filter( name = "member" )[0]
        Rule( acl_action_id = action.id, acl_role_id = role.id, allow = False ).add()

        self.assertRaises( AccessDenied, UserProfile.filter, users_account_id = member.id )
