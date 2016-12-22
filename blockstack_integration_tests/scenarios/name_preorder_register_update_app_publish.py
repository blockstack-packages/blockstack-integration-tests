#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Blockstack
    ~~~~~
    copyright: (c) 2014-2015 by Halfmoon Labs, Inc.
    copyright: (c) 2016 by Blockstack.org

    This file is part of Blockstack

    Blockstack is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Blockstack is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with Blockstack. If not, see <http://www.gnu.org/licenses/>.
""" 
import os
import testlib
import pybitcoin
import urllib2
import json
import blockstack_client
import blockstack_profiles
import blockstack_gpg
import sys

wallets = [
    testlib.Wallet( "5JesPiN68qt44Hc2nT8qmyZ1JDwHebfoh9KQ52Lazb1m1LaKNj9", 100000000000 ),
    testlib.Wallet( "5KHqsiU9qa77frZb6hQy9ocV7Sus9RWJcQGYYBJJBb2Efj1o77e", 100000000000 ),
    testlib.Wallet( "5Kg5kJbQHvk1B64rJniEmgbD83FpZpbw2RjdAZEzTefs9ihN3Bz", 100000000000 ),
    testlib.Wallet( "5JuVsoS9NauksSkqEjbUZxWwgGDQbMwPsEfoRBSpLpgDX1RtLX7", 100000000000 ),
    testlib.Wallet( "5KEpiSRr1BrT8vRD7LKGCEmudokTh1iMHbiThMQpLdwBwhDJB1T", 100000000000 ),
    testlib.Wallet( "5K5hDuynZ6EQrZ4efrchCwy6DLhdsEzuJtTDAf3hqdsCKbxfoeD", 100000000000 ),
    testlib.Wallet( "5J39aXEeHh9LwfQ4Gy5Vieo7sbqiUMBXkPH7SaMHixJhSSBpAqz", 100000000000 ),
    testlib.Wallet( "5K9LmMQskQ9jP1p7dyieLDAeB6vsAj4GK8dmGNJAXS1qHDqnWhP", 100000000000 ),
    testlib.Wallet( "5KcNen67ERBuvz2f649t9F2o1ddTjC5pVUEqcMtbxNgHqgxG2gZ", 100000000000 )
]

consensus = "17ac43c1d8549c3181b200f1bf97eb7d"
wallet_keys = None
error = False

index_file_data = "<html><head></head><body>foo.test hello world</body></html>"
resource_data = "hello world"

def scenario( wallets, **kw ):

    global wallet_keys, error, index_file_data, resource_data

    testlib.blockstack_namespace_preorder( "test", wallets[1].addr, wallets[0].privkey )
    testlib.next_block( **kw )

    testlib.blockstack_namespace_reveal( "test", wallets[1].addr, 52595, 250, 4, [6,5,4,3,2,1,0,0,0,0,0,0,0,0,0,0], 10, 10, wallets[0].privkey )
    testlib.next_block( **kw )

    testlib.blockstack_namespace_ready( "test", wallets[1].privkey )
    testlib.next_block( **kw )

    testlib.blockstack_name_preorder( "foo.test", wallets[2].privkey, wallets[3].addr )
    testlib.next_block( **kw )
    
    testlib.blockstack_name_register( "foo.test", wallets[2].privkey, wallets[3].addr )
    testlib.next_block( **kw )

    test_proxy = testlib.TestAPIProxy()
    blockstack_client.set_default_proxy( test_proxy )
    wallet_keys = blockstack_client.make_wallet_keys( payment_privkey=wallets[5].privkey, owner_privkey=wallets[3].privkey, data_privkey=wallets[4].privkey )
    wallet = testlib.blockstack_client_initialize_wallet( "0123456789abcdef", wallets[5].privkey, wallets[3].privkey, wallets[4].privkey )
    
    # migrate profiles 
    res = testlib.migrate_profile( "foo.test", proxy=test_proxy, wallet_keys=wallet_keys )
    if 'error' in res:
        res['test'] = 'Failed to initialize foo.test profile'
        print json.dumps(res, indent=4, sort_keys=True)
        error = True
        return 

    # tell serialization-checker that value_hash can be ignored here
    print "BLOCKSTACK_SERIALIZATION_CHECK_IGNORE value_hash"
    sys.stdout.flush()
    
    testlib.next_block( **kw )

    data_pk = wallets[-1].privkey
    data_pub = wallets[-1].pubkey_hex
    
    config_path = os.environ.get("BLOCKSTACK_CLIENT_CONFIG", None)

    # make an index file 
    index_file_path = "/tmp/name_preorder_register_update_app_publish.foo.test.index.html"
    with open(index_file_path, "w") as f:
        f.write(index_file_data)

    # register an application 
    res = testlib.blockstack_cli_app_publish("foo.test", "get_mutable,put_mutable,delete_mutable", index_file_path, appname="bar", drivers="disk", password="0123456789abcdef" )
    if 'error' in res:
        res['test'] = 'Failed to register foo.test/bar app'
        print json.dumps(res, indent=4, sort_keys=True)
        error = True
        return 

    # put mutable data, to be accessed as a resource
    resource_file_path = "/tmp/name_preorder_register_update_app_publish.foo.test.resource"
    with open(resource_file_path, "w") as f:
        f.write(resource_data)

    res = testlib.blockstack_cli_app_put_resource("foo.test", "hello_world", resource_file_path, appname="bar" )
    if 'error' in res:
        res['test'] = 'Failed to store app resource'
        print json.dumps(res, indent=4, sort_keys=True)
        error = True
        return 

    testlib.next_block( **kw )



def check( state_engine ):

    global wallet_keys, error, index_file_data, resource_data

    if error:
        print "Key operation failed."
        return False

    # not revealed, but ready 
    ns = state_engine.get_namespace_reveal( "test" )
    if ns is not None:
        print "namespace not ready"
        return False 

    ns = state_engine.get_namespace( "test" )
    if ns is None:
        print "no namespace"
        return False 

    if ns['namespace_id'] != 'test':
        print "wrong namespace"
        return False 

    names = ['foo.test']
    wallet_keys_list = [wallet_keys]
    test_proxy = testlib.TestAPIProxy()

    for i in xrange(0, len(names)):
        name = names[i]
        wallet_payer = 3 * (i+1) - 1
        wallet_owner = 3 * (i+1)
        wallet_data_pubkey = 3 * (i+1) + 1
        wallet_keys = wallet_keys_list[i]

        # not preordered
        preorder = state_engine.get_name_preorder( name, pybitcoin.make_pay_to_address_script(wallets[wallet_payer].addr), wallets[wallet_owner].addr )
        if preorder is not None:
            print "still have preorder"
            return False
    
        # registered 
        name_rec = state_engine.get_name( name )
        if name_rec is None:
            print "name does not exist"
            return False 

        # owned 
        if name_rec['address'] != wallets[wallet_owner].addr or name_rec['sender'] != pybitcoin.make_pay_to_address_script(wallets[wallet_owner].addr):
            print "name has wrong owner"
            return False 

        # get app config 
        app_config = testlib.blockstack_cli_app_get_config( "foo.test", appname="bar" )
        if 'error' in app_config:
            print "failed to get app config\n{}\n".format(json.dumps(app_config, indent=4, sort_keys=True))
            return False

        # inspect...
        app_config = app_config['config']

        if app_config['driver_hints'] != ['disk']:
            print "Invalid driver hints\n{}\n".format(json.dumps(app_config, indent=4, sort_keys=True))
            return False

        if app_config['api_methods'] != ['get_mutable', 'put_mutable', 'delete_mutable']:
            print "Invalid API list\n{}\n".format(json.dumps(app_config, indent=4, sort_keys=True))
            return False

        if len(app_config['index_uris']) != 1:
            print "Invalid URI records\n{}\n".format(json.dumps(app_config, indent=4, sort_keys=True))
            return False

        # get index file 
        index_file = testlib.blockstack_cli_app_get_index_file("foo.test", appname="bar")
        if 'error' in index_file:
            print "failed to get index file\n{}\n".format(json.dumps(index_file, indent=4, sort_keys=True))
            return False
        
        if index_file['index_file'] != index_file_data:
            print "got wrong index file:\n{}\n".format(index_file['index_file'])
            return False

        # get resource 
        resource_data_res = testlib.blockstack_cli_app_get_resource("foo.test", "hello_world", appname="bar")
        if 'error' in resource_data_res:
            print "failed to get resource hello_world\n{}\n".format(json.dumps(resource_data, indent=4, sort_keys=True))
            return False

        if resource_data_res['res'] != resource_data:
            print "got wrong resource data:\n{}\nexpected:\n{}\n".format(resource_data_res['res'], resource_data)
            return False

    return True
