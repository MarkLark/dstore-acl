from dstore import Model, var, mod


class Role( Model ):
    _namespace = "acl.role"
    _vars = [
        var.RowID,
        var.String( "name", 32, mods = [ mod.NotNull() ] )
    ]


class UserRole( Model ):
    _namespace = "acl.user_role"
    _vars = [
        var.RowID,
        var.ForeignKey( "acl.role" ),
        var.Number( "user_id", mods = [ mod.NotNull() ] )
    ]


class Rule( Model ):
    _namespace = "acl.rule"
    _vars = [
        var.RowID,
        var.ForeignKey( "acl.role" ),
        var.ForeignKey( "acl.action" ),
        var.Boolean( "allow", True )
    ]


class Action( Model ):
    _namespace = "acl.action"
    _vars = [
        var.RowID,
        var.String( "model", 32, mods = [ mod.NotNull() ] ),
        var.String( "name", 32, mods = [ mod.NotNull() ] ),
        var.Boolean( "fallback", False )
    ]
