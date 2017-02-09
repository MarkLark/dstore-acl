from nose.tools import eq_, raises
from . import BaseTest, Model, var, mod
from dstore_acl import Rule, Role, Action


class ACL_Rules( BaseTest ):
    def test_car_actions( self ):
        num_actions = 0
        for action in Action.filter( model = "cars.make" ):
            print( "ACL_Rules: %s" % action.name )
            if   action.name == "add"   : eq_( action.fallback, False, "cars.make:add[default] should be False"    )
            elif action.name == "read"  : eq_( action.fallback, True,  "cars.make:read[default] should be True"    )
            elif action.name == "update": eq_( action.fallback, False, "cars.make:update[default] should be False" )
            elif action.name == "delete": eq_( action.fallback, False, "cars.make:delete[default] should be False" )
            elif action.name == "empty" : eq_( action.fallback, False, "cars.make:empty[default] should be False"  )
            num_actions += 1
        eq_( num_actions, 5, "cars.make: There should be 4 actions defined not %d" % num_actions )

    def test_car_rules( self ):
        actions = {}
        roles   = {}
        for action in Action.filter( model = "cars.make" ): actions[ action.name ] = action
        for role in Role.all(): roles[ role.id ] = role

        # Test add rules
        eq_( actions[ "add" ].fallback, False, "cars.make:add[default] should be False" )
        num_rules = 0
        for rule in Rule.filter( acl_action_id = actions[ "add" ].id ):
            role = roles[ rule.acl_role_id ]
            if   role.name == "admin" : eq_( rule.allow, True, "cars.make:add[admin] should be True"  )
            elif role.name == "member": eq_( rule.allow, True, "cars.make:add[member] should be True" )
            else                      : eq_( 0, 1, "cars.make:add[%s] Role should not have a rule defined" % role.name )
            num_rules += 1
        eq_( num_rules, 2, "cars.make:add: There should be 2 rules defined not %d" % num_rules )

        # Test read rules
        eq_( actions[ "read" ].fallback, True, "cars.make:read[default] should be True" )

        # Test Update rules
        eq_( actions[ "update" ].fallback, False, "cars.make:update[default] should be False" )
        num_rules = 0
        for rule in Rule.filter( acl_action_id = actions[ "update" ].id ):
            role = roles[ rule.acl_role_id ]
            if role.name == "admin": eq_( rule.allow, True, "cars.make:update[admin] should be True" )
            else                   : eq_( 0, 1, "cars.make:update[%s] Role should not have a rule defined" % role.name )
            num_rules += 1
        eq_( num_rules, 1, "cars.make:update: There should be 1 rule defined not %d" % num_rules )

        eq_( actions[ "delete" ].fallback, False, "cars.make:delete[default] should be False" )
        num_rules = 0
        for rule in Rule.filter( acl_action_id = actions[ "delete" ].id ):
            role = roles[ rule.acl_role_id ]
            if role.name == "admin": eq_( rule.allow, True, "cars.make:delete[admin] should be True" )
            else                   : eq_( 0, 1, "cars.make.delete[%s] Role should not have a rule defined" % role.name )
            num_rules += 1
        eq_( num_rules, 1, "cars.make:delete: There should be 1 rule defined not %d" % num_rules )

        eq_( actions[ "empty" ].fallback, False, "cars.make:empty[default] should be False" )
        num_rules = 0
        for rule in Rule.filter( acl_action_id = actions[ "empty" ].id ):
            role = roles[ rule.acl_role_id ]
            if role.name == "admin": eq_( rule.allow, True, "cars.make:empty[admin] should be True" )
            else                   : eq_( 0, 1, "cars.make:empty[%s] Role should not have a rule defined" % role.name )
            num_rules += 1
        eq_( num_rules, 1, "cars.make:empty: There should be 1 rule defined not %d" % num_rules )

    def test_auto_update_rule( self ):
        action = Action.filter( model = "cars.make", name = "add" )[0]

        rule_before = Rule.filter( acl_action_id = action.id, acl_role_id = 0 )[0]
        Rule( acl_action_id = action.id, acl_role_id = 0, allow = False ).add()

        rule = Rule.get( rule_before.id )

        eq_( rule.allow, False, "The rule should be allow=False" )
