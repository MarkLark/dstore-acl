from dstore import Model, var, mod


class Car( Model ):
    _namespace = "cars.make"
    _vars = [
        var.RowID,
        var.String( "manufacturer", 32, mods = [ mod.NotNull() ] ),
        var.String( "make", 32, mods = [ mod.NotNull() ] ),
        var.Number( "year", mods = [ mod.NotNull(), mod.Min( 1950 ), mod.Max( 2017 ) ] ),
    ]
    _acl_rules = dict(
        add    = dict( allow = [ "admin", "member" ]),
        read   = dict( default = True ),
        update = dict( allow = [ "admin" ]),
        delete = dict( allow = [ "admin" ]),
        empty  = dict( allow = [ "admin" ])
    )


class UserAccount( Model ):
    _namespace = "users.account"
    _vars = [
        var.RowID,
        var.String( "name", 32, mods = [ mod.NotNull() ])
    ]
    _acl_rules = dict(
        add_own       = dict( default = True ),
        add_others    = dict( default = True ),
        read_own      = dict( allow = [ "admin", "member" ] ),
        read_others   = dict( allow = [ "admin" ] ),
        update_own    = dict( allow = [ "admin", "member" ] ),
        delete_own    = dict( allow = [ "admin" ] ),
        delete_others = dict( allow = [ "admin" ] ),
        empty         = dict( allow = [ "admin" ])
    )


class UserProfile( Model ):
    _namespace = "users.profile"
    _vars = [
        var.RowID,
        var.String( "nickname", 32, mods = [ mod.NotNull() ]),
        var.ForeignKey( "users.account" )
    ]
    _acl_rules = dict(
        add_own       = dict( default = True ),
        add_others    = dict( allow = [ "admin" ]),
        read_own      = dict( default = True ),
        read_others   = dict( allow = [ "admin" ]),
        update_own    = dict( default = True ),
        update_others = dict( allow = [ "admin" ]),
        delete_own    = dict( default = True ),
        delete_others = dict( allow = [ "admin" ]),
        empty         = dict( allow = [ "admin" ])
    )
