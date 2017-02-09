from .BaseACL import BaseACL


class ModelACL( BaseACL ):
    def __init__( self, acl, model ):
        super( ModelACL, self ).__init__( acl, model )
        self.actions = [
            "add",
            "read",
            "update",
            "delete",
            "empty"
        ]

    def _before_empty( self, event, model ):
        self( "empty" )

    def _before_add( self, event, model, instance ):
        self( "add" )

    def _before_update( self, event, model, instance ):
        self( "update" )

    def _before_delete( self, event, model, instance ):
        self( "delete" )

    def _after_all( self, event, model, instances ):
        self( "read" )

    def _after_get( self, event, model, instance ):
        action = "read"
        self( action )

    def _after_filter( self, event, model, instances, params ):
        self( "read" )
