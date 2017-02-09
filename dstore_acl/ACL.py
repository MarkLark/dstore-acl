from . import Role, Action, Rule, UserRole
from .ModelACL import ModelACL
from .UserACL import UserACL
from dstore.Error import InstanceNotFound, VariableNotFound


class ACL( object ):
    def __init__( self, data_store, get_user, user_model ):
        self.data_store = data_store
        self.get_user   = get_user
        self.user_model = user_model
        self.models     = {}

        self.data_store.models.insert( 0, UserRole )
        self.data_store.models.insert( 0, Rule     )
        self.data_store.models.insert( 0, Role     )
        self.data_store.models.insert( 0, Action   )

        self.data_store.events.before_init_app += self.before_init_app

    def before_init_app( self, event, store ):
        self.data_store.events.after_register_model += self.after_register_model
        Rule.events.before_add += self.before_add_rule

    def after_register_model( self, event, store, model ):
        if model in [ Action, Role, Rule, UserRole ]: return
        self.models[ model._namespace ] = model

        # Get the Variable Name that references the User Model
        if model == self.user_model:
            user_var_name = "id"
        else:
            user_var_name = "%s_id" % self.user_model._namespace.replace(".", "_")

        # Attempt to get the Variable that references the User Model
        # If it is not found, then this Model does not reference a User Instance
        # And therefor cannot be owned by a User, so we instantiate a ModelACL
        # Otherwise we instantiate a UserACL
        try:
            model.get_var( user_var_name )
            model.acl = UserACL( self, model, user_var_name )
        except VariableNotFound:
            model.acl = ModelACL( self, model )

    def before_add_rule( self, event, model, instance ):
        # We need to check if there are any rules for this role and action
        # If so, we update the current rule, and deny adding this one
        try:
            rule = Rule.filter( acl_role_id = instance.acl_role_id, acl_action_id = instance.acl_action_id )[0]
            rule.allow = instance.allow
            rule.update()
            event.cancel()
        except InstanceNotFound:
            pass
