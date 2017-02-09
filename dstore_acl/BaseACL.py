from . import Role, Action, Rule, UserRole, AccessDenied, ActionNotFound
from dstore.Error import InstanceNotFound


class BaseACL( object ):
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

    def __getattr__( self, name ):
        not_acl = [ "acl", "model", "get_user", "user_model", "actions", "user_var_id" ]
        if name in not_acl: return self.__dict__[ name ]
        if name not in self.actions: raise ActionNotFound( self.model, name )
        try:
            return Action.filter( model = self.model._namespace, name = name )[0]
        except InstanceNotFound:
            raise ActionNotFound( self.model, name )

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

    def _before_empty( self, event, model ):
        raise NotImplementedError("Must implement _before_empty method")

    def _before_add( self, event, model, instance ):
        raise NotImplementedError( "Must implement _before_add method" )

    def _before_update( self, event, model, instance ):
        raise NotImplementedError( "Must implement _before_update method" )

    def _before_delete( self, event, model, instance ):
        raise NotImplementedError("Must implement _before_delete method")

    def _after_all( self, event, model, instances ):
        raise NotImplementedError("Must implement _after_all method")

    def _after_get( self, event, model, instance ):
        raise NotImplementedError("Must implement _after_get method")

    def _after_filter( self, event, model, instances, params ):
        raise NotImplementedError("Must implement _after_filter method")

    def _get_action( self, action, throw_error = True ):
        if isinstance( action, str ):
            try:
                action = Action.filter( name = action, model = self.model._namespace )[0]
            except InstanceNotFound:
                if throw_error: raise AccessDenied( self.model._store, self.model, action )
                return False
        elif not isinstance( action, Action ):
            raise RuntimeError( "Incorrect Action instance supplied" )

        return action

    def _get_role( self, role, throw_error = True ):
        if isinstance( role, str ):
            try:
                role = Role.filter( name = role )[0]
            except InstanceNotFound:
                if throw_error: raise AccessDenied( self.model._store, self.model, "" )
                return False
        elif not isinstance( role, Role ):
            raise RuntimeError( "Incorrect Role instance supplied. %s.%s" )

        return role

    def __call__( self, action, role = None, throw_error = True ):
        if role is None: user, role = self._get_role_from_user()

        action = self._get_action( action, throw_error )
        if not action: return False

        if role is None:
            if throw_error and not action.fallback: raise AccessDenied( self.model._store, self.model, action )
            return action.fallback

        role = self._get_role( role, throw_error )
        if not role: return action.fallback

        try:
            rule = Rule.filter( acl_role_id = role.id, acl_action_id = action.id )[0]
        except InstanceNotFound:
            if not action.fallback and throw_error: raise AccessDenied( self.model._store, self.model, action )
            return action.fallback

        if throw_error and not rule.allow: raise AccessDenied( self.model._store, self.model, action )
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
