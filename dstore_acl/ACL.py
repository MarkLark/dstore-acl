from . import Role, Action, Rule, UserRole
from .ACLHelper import ACLHelper
from dstore.Error import InstanceNotFound


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
        model.acl = ACLHelper( self, model )

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
