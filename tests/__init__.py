from dstore import MemoryStore, Model, var, mod
from unittest import TestCase
from dstore_acl import ACL, Role, UserRole
from .models import Car, UserAccount, UserProfile
from dstore.Error import InstanceNotFound


__all__ = [ "BaseTest", "Car", "AllVars", "User" ]


class BaseTest( TestCase ):
    models      = [ Car, UserAccount ]
    auto_create = True
    auto_init   = True
    auto_add_users = False

    def get_store( self ):
        return MemoryStore( list( self.models ) )

    def set_config( self ):
        pass

    def setUp( self ):
        self.store = self.get_store()
        self.users = {}
        self.user  = "admin"

        self.acl = ACL(
            data_store = self.store,
            get_user   = self.get_user,
            user_model = UserAccount
        )

        self.store.init_app()
        self.set_config()
        self.store.connect()

        self.store.create_all()

        if self.auto_add_users: self.add_users()

    def tearDown( self ):
        self.store.destroy_all()
        self.store.disconnect()
        self.store.destroy_app()

    def get_user( self, name = None ):
        if name is not None: self.user = name
        return self.users.get( self.user, None )

    def add_users( self ):
        for t in [ "admin", "member", "guest" ]:
            self.users[ t ] = UserAccount( name = t ).add()
            try:
                role = Role.filter( name = t )[0]
                UserRole( user_id = self.users[ t ].id, acl_role_id = role.id ).add()
            except InstanceNotFound:
                pass
