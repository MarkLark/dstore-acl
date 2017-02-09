from .ModelACL import ModelACL
from . import AccessDenied


class UserACL( ModelACL ):
    def __init__( self, acl, model, user_var_name ):
        super( UserACL, self ).__init__( acl, model )

        self.user_var_id = user_var_name
        self.user_model  = self.acl.user_model

        # Override the default actions from ModelACL
        # To provide Actions based around User ownership
        self.actions = [
            "add_own",
            "add_others",
            "read_own",
            "read_others",
            "update_own",
            "update_others",
            "delete_own",
            "delete_others",
            "empty"
        ]

    def _before_add( self, event, model, instance ):
        if self._owns_instance( instance ): self("add_own")
        else                              : self("add_others")

    def _before_update( self, event, model, instance ):
        if self._owns_instance( instance ): self("update_own")
        else                              : self("update_others")

    def _before_delete( self, event, model, instance ):
        if self._owns_instance( instance ): self("delete_own")
        else                              : self("delete_others")

    def _after_all( self, event, model, instances ):
        self._filter_read_list( instances )
        if len( instances ) == 0: raise AccessDenied( model._store, model, "all" )

    def _after_get( self, event, model, instance ):
        if self._owns_instance( instance ): self("read_own")
        else                              : self("read_others")

    def _after_filter( self, event, model, instances, params ):
        self._filter_read_list( instances )
        if len( instances ) == 0: raise AccessDenied( model._store, model, "filter" )

    def _filter_read_list( self, instances ):
        user, role  = self._get_role_from_user()
        read_own    = self( "read_own",    role, False )
        read_others = self( "read_others", role, False )

        i = 0
        for instance in list( instances ):
            if self._owns_instance( instance, user ):
                if not read_own:
                    instances.pop( i )
                    continue
            else:
                if not read_others:
                    instances.pop( i )
                    continue
            i += 1

    def _owns_instance( self, instance, user = None ):
        if user is None: user = self.get_user()
        owner_id = instance.__dict__[ self.user_var_id ]

        if user is None: return False
        elif user.id == owner_id: return True
        return False