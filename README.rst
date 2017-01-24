Welcome To DStore-ACL
#####################

.. image:: https://img.shields.io/coveralls/MarkLark/dstore-acl.svg
    :target: https://coveralls.io/github/MarkLark/dstore-acl?branch=master

.. image:: https://img.shields.io/travis/MarkLark/dstore-acl/master.svg
    :target: https://travis-ci.org/MarkLark/dstore-acl

.. image:: https://img.shields.io/pypi/v/dstore-acl.svg
    :target: https://pypi.python.org/pypi/dstore-acl

.. image:: https://img.shields.io/pypi/pyversions/dstore-acl.svg
    :target: https://pypi.python.org/pypi/dstore-acl

DStore-ACL is a Security Layer for DStore.


Installing
==========

DStore-ACL is available from the PyPi repository.

This means that all you have to do to install DStore-ACL is run the following in a console:

.. code-block:: console

    $ pip install dstore-acl

Minimal Example
===============

.. code-block:: python

    from dstore import MemoryStore, Model, var, mod
    from dstore_acl import ACL, Role, UserRole, AccessDenied


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


    class Car( Model ):
        _namespace = "cars.make"
        _vars = [
            var.RowID,
            var.String( "manufacturer", 32, mods = [ mod.NotNull() ] ),
            var.String( "make", 32, mods = [ mod.NotNull() ] ),
            var.Number( "year", mods = [ mod.NotNull(), mod.Min( 1950 ), mod.Max( 2017 ) ] ),
        ]
        _acl_rules = dict(
            add    = dict( allow = [ "admin" ]),
            read   = dict( default = True ),
            update = dict( allow = [ "admin" ]),
            delete = dict( allow = [ "admin" ]),
            empty  = dict( allow = [ "admin" ])
        )

    users = {}
    current_user = "admin"

    # Create the MemoryStore instance, and add Models to it
    store = MemoryStore( [ Car ] )

    acl = ACL(
        data_store = store,
        get_user   = get_user,
        user_model = UserAccount
    )

    store.init_app()
    store.connect()
    store.create_all()

    # Create the user accounts
    for name in [ "admin", "member" ]:
        users[ name ] = UserAccount( name = name ).add()
        role = Role.filter( name = name )[0]
        UserRole( user_id = users[ name ].id, acl_role_id = role.id ).add()

    # Admin can add new cars
    Car( manufacturer = "Holden", make = "Commodore", year = 2009 ).add()

    # Member cannot add new cars
    current_user = "member"
    try:
        Car( manufacturer = "Holden", make = "Commodore", year = 2010 ).add()
    except AccessDenied:
        pass

    # Destroy all instances and shut down the application
    store.destroy_all()
    store.disconnect()
    store.destroy_app()

    def get_user():
        return users[ current_user ]


Documentation: `ReadTheDocs <http://dstore-acl.readthedocs.io/>`_

Source Code: `GitHub <https://github.com/MarkLark/dstore-acl>`_
