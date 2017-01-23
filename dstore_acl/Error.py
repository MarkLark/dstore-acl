
class AccessDenied( Exception ): pass


class ActionNotFound( Exception ):
    def __init__( self, model, action ):
        super( ActionNotFound, self ).__init__(
            "ACL Action %s.%s not found" % ( model._namespace, action )
        )
