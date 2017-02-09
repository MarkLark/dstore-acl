from dstore.Error import ModelError


class AccessDenied( ModelError ):
    def __init__( self, store, model, action ):
        super( AccessDenied, self ).__init__(
            store,
            model,
            "Access denied to %s %s.%s" % (action, store.name, model._namespace)
        )


class ActionNotFound( Exception ):
    def __init__( self, model, action ):
        super( ActionNotFound, self ).__init__(
            "ACL Action %s.%s not found" % ( model._namespace, action )
        )
