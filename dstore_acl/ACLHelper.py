from . import Role, Action, Rule, UserRole, AccessDenied, ActionNotFound
from dstore.Error import InstanceNotFound


class ACLHelper( object ):
    def __init__( self, acl, model ):
        self.acl        = acl
        self.model      = model
        self.get_user   = self.acl.get_user

        self.model.events.after_create  += self._after_create
        self.model.events.before_add    += self._before_add
        self.model.events.before_update += self._before_update
        self.model.events.before_delete += self._before_delete
        self.model.events.before_empty  += self._before_empty

        self.model.events.after_all     += self._after_all
        self.model.events.after_get     += self._after_get
        self.model.events.after_filter  += self._after_filter

        var_name = "%s_id" % self.acl.user_model._namespace.replace( ".", "_" )
        var = self.model.get_var( var_name )

        if var is not None or self.model == self.acl.user_model:
            if self.model == self.acl.user_model: self.user_var_id = "id"
            else                                : self.user_var_id = var_name

            self.user_model = self.acl.user_model
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
        else:
            self.user_model  = None
            self.user_var_id = None
            self.actions = [
                "add",
                "read",
                "update",
                "delete",
                "empty"
            ]

    def __getattr__( self, name ):
        not_acl = [ "acl", "model", "get_user", "user_model", "actions", "user_var_id" ]
        if name in not_acl: return self.__dict__[ name ]
        if name not in self.actions: raise ActionNotFound( self.model, name )
        return Action.filter( model = self.model._namespace, name = name )[0]

    def _has_actions( self ):
        try:
            Action.filter( model = self.model._namespace, name = self.actions[0] )
        except InstanceNotFound:
            return False
        return True

    def _get_role_from_user( self ):
        user = self.get_user()
        if user is None: return None, None
        try:
            userrole = UserRole.filter( user_id = user.id )[0]
            role     = Role.get( userrole.acl_role_id )
        except InstanceNotFound:
            return None, None
        return user, role

    def _add_actions( self ):
        if self._has_actions(): return
        for action in self.actions:
            Action( model = self.model._namespace, name = action ).add()

    def _add_default_rules( self ):
        if not hasattr( self.model, "_acl_rules" ): return
        self.add_rules( self.model._acl_rules )

    def _after_create( self, event, model ):
        self._add_actions()
        self._add_default_rules()

    def _owns_instance( self, instance, user = None ):
        if user is None: user = self.get_user()
        owner_id = instance.__dict__[ self.user_var_id ]

        if user is None: return False
        elif user.id == owner_id: return True
        return False

    def _before_empty( self, event, model ):
        self( "empty" )

    def _before_add( self, event, model, instance ):
        action = "add"
        if self.user_model is not None:
            if self._owns_instance( instance ): action = "add_own"
            else                              : action = "add_others"
        self( action )

    def _before_update( self, event, model, instance ):
        action = "update"
        if self.user_model is not None:
            if self._owns_instance( instance ): action = "update_own"
            else                              : action = "update_others"
        self( action )

    def _before_delete( self, event, model, instance ):
        action = "delete"
        if self.user_model is not None:
            if self._owns_instance( instance ): action = "delete_own"
            else                              : action = "delete_others"
        self( action )

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

    def _after_all( self, event, model, instances ):
        if self.user_model is None: self( "read" )
        else:
            self._filter_read_list( instances )
            if len( instances ) == 0: raise AccessDenied()

    def _after_get( self, event, model, instance ):
        action = "read"
        if self.user_model is not None:
            if self._owns_instance( instance ): action = "read_own"
            else                              : action = "read_others"
        self( action )

    def _after_filter( self, event, model, instances, params ):
        if self.user_model is None: self( "read" )
        else:
            self._filter_read_list( instances )
            if len( instances ) == 0: raise AccessDenied()

    def _get_action( self, action, throw_error = True ):
        if isinstance( action, str ):
            try:
                action = Action.filter( name = action, model = self.model._namespace )[0]
            except InstanceNotFound:
                if throw_error: raise AccessDenied()
                return False
        elif not isinstance( action, Action ):
            raise RuntimeError( "Incorrect Action instance supplied" )

        return action

    def _get_role( self, role, throw_error = True ):
        if isinstance( role, str ):
            try:
                role = Role.filter( name = role )[0]
            except InstanceNotFound:
                if throw_error: raise AccessDenied()
                return False
        elif not isinstance( role, Role ):
            raise RuntimeError( "Incorrect Role instance supplied. %s.%s" )

        return role

    def __call__( self, action, role = None, throw_error = True ):
        if role is None: user, role = self._get_role_from_user()

        action = self._get_action( action, throw_error )
        if not action: return False

        if role is None:
            if throw_error and not action.fallback: raise AccessDenied()
            return action.fallback

        role = self._get_role( role, throw_error )
        if not role: return action.fallback

        try:
            rule = Rule.filter( acl_role_id = role.id, acl_action_id = action.id )[0]
        except InstanceNotFound:
            if not action.fallback and throw_error: raise AccessDenied()
            return action.fallback

        if throw_error and not rule.allow: raise AccessDenied()
        return rule.allow

    def add_rules( self, rules ):
        roles   = {}
        actions = {}

        for action_name in rules:
            if action_name not in actions:
                try:
                    actions[ action_name ] = Action.filter( name = action_name, model = self.model._namespace )[0]
                except InstanceNotFound:
                    actions[ action_name ] = Action( name = action_name, model = self.model._namespace ).add()
            action = actions[ action_name ]

            for allow_name in rules[ action_name ]:
                if allow_name == "default":
                    action.fallback = rules[ action_name ][ allow_name ]
                    action.update()
                    continue

                elif allow_name == "allow": allow = True
                else                      : allow = False

                for role_name in rules[ action_name ][ allow_name ]:
                    if role_name not in roles:
                        try:
                            roles[ role_name ] = Role.filter( name = role_name )[0]
                        except InstanceNotFound:
                            roles[ role_name ] = Role( name = role_name ).add()
                    role = roles[ role_name ]

                    Rule( acl_role_id = role.id, acl_action_id = action.id, allow = allow ).add()
