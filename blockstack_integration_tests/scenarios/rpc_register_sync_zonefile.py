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

import testlib
import pybitcoin
import time
import json
import sys
import os
import blockstack_client
import blockstack_zones
import base64

wallets = [
    testlib.Wallet( "5JesPiN68qt44Hc2nT8qmyZ1JDwHebfoh9KQ52Lazb1m1LaKNj9", 100000000000 ),
    testlib.Wallet( "5KHqsiU9qa77frZb6hQy9ocV7Sus9RWJcQGYYBJJBb2Efj1o77e", 100000000000 ),
    testlib.Wallet( "5Kg5kJbQHvk1B64rJniEmgbD83FpZpbw2RjdAZEzTefs9ihN3Bz", 100000000000 ),
    testlib.Wallet( "5JuVsoS9NauksSkqEjbUZxWwgGDQbMwPsEfoRBSpLpgDX1RtLX7", 5500 ),
    testlib.Wallet( "5KEpiSRr1BrT8vRD7LKGCEmudokTh1iMHbiThMQpLdwBwhDJB1T", 5500 )
]

consensus = "17ac43c1d8549c3181b200f1bf97eb7d"
zonefile_hash = None

def scenario( wallets, **kw ):

    global zonefile_hash

    testlib.blockstack_namespace_preorder( "test", wallets[1].addr, wallets[0].privkey )
    testlib.next_block( **kw )

    testlib.blockstack_namespace_reveal( "test", wallets[1].addr, 52595, 250, 4, [6,5,4,3,2,1,0,0,0,0,0,0,0,0,0,0], 10, 10, wallets[0].privkey )
    testlib.next_block( **kw )

    testlib.blockstack_namespace_ready( "test", wallets[1].privkey )
    testlib.next_block( **kw )

    wallet = testlib.blockstack_client_initialize_wallet( "0123456789abcdef", wallets[2].privkey, wallets[3].privkey, wallets[4].privkey )
    resp = testlib.blockstack_cli_register( "foo.test", "0123456789abcdef" )
    if 'error' in resp:
        print >> sys.stderr, json.dumps(resp, indent=4, sort_keys=True)
        return False
   
    # wait for the preorder to get confirmed
    for i in xrange(0, 12):
        testlib.next_block( **kw )

    # wait for the poller to pick it up
    print >> sys.stderr, "Waiting 10 seconds for the backend to submit the register"
    time.sleep(10)


    # wait for the register to get confirmed 
    for i in xrange(0, 12):
        # warn the serialization checker that this changes behavior from 0.13
        print "BLOCKSTACK_SERIALIZATION_CHECK_IGNORE value_hash"
        sys.stdout.flush()
        
        testlib.next_block( **kw )

    print >> sys.stderr, "Waiting 10 seconds for the backend to acknowledge registration"
    time.sleep(10)

    # wait for initial update to get confirmed 
    for i in xrange(0, 12):
        # warn the serialization checker that this changes behavior from 0.13
        print "BLOCKSTACK_SERIALIZATION_CHECK_IGNORE value_hash"
        sys.stdout.flush()
        
        testlib.next_block( **kw )

    print >> sys.stderr, "Waiting 10 seconds for the backend to acknowledge update"
    time.sleep(10)
    
    # store a new zonefile
    data_pubkey = wallet['data_pubkey']
    zonefile = blockstack_client.user.make_empty_user_zonefile( "foo.test", data_pubkey )
    assert blockstack_client.user.put_immutable_data_zonefile( zonefile, "testdata", blockstack_client.get_data_hash("testdata") )

    zonefile_txt = blockstack_zones.make_zone_file( zonefile )
    zonefile_hash = blockstack_client.storage.get_zonefile_data_hash( zonefile_txt )
   
    print >> sys.stderr, "\n\nzonefile hash: %s\nzonefile:\n%s\n\n" % (zonefile_hash, zonefile_txt)

    # will store to queue
    test_proxy = testlib.make_proxy()
    config_path = test_proxy.config_path
    conf = blockstack_client.config.get_config(config_path)
    queuedb_path = conf['queue_path']

    # update the zonefile hash, but not the zonefile.
    resp = testlib.blockstack_cli_set_zonefile_hash( "foo.test", zonefile_hash )
    if 'error' in resp:
        print >> sys.stderr, "\nFailed to set zonefile hash: %s\n" % resp
        return False

    txhash = resp['transaction_hash']
    for i in xrange(0, 12):
        # warn the serialization checker that this changes behavior from 0.13
        print "BLOCKSTACK_SERIALIZATION_CHECK_IGNORE value_hash"
        sys.stdout.flush()
        
        testlib.next_block( **kw )

    print >> sys.stderr, "Waiting 10 seconds for the backend to acknowledge update"
    time.sleep(10)

    # stop endpoint
    print >> sys.stderr, "\nstopping RPC daemon\n"
    config_dir = os.path.dirname(test_proxy.config_path)

    blockstack_client.rpc.local_rpc_stop(config_dir=config_dir)
    time.sleep(3)

    # store to queue
    res = blockstack_client.backend.queue.queue_append("update", "foo.test", txhash, payment_address=wallets[2].addr, owner_address=wallets[3].addr,
                                                       config_path=test_proxy.config_path, zonefile_data=zonefile_txt, zonefile_hash=zonefile_hash, path=queuedb_path )

    # verify that we can sync the zonefile, using the in-queue zonefile
    resp = testlib.blockstack_cli_sync_zonefile( "foo.test" )
    if 'error' in resp:
        print >> sys.stderr, "\nfailed to sync zonefile: %s\n" % resp
        return False

    blockstack_client.backend.queue.queuedb_remove("update", "foo.test", txhash, path=queuedb_path )

    print >> sys.stderr, "\nstarting RPC daemon\n"
    blockstack_client.actions.start_rpc_endpoint(config_dir, password="0123456789abcdef")
    time.sleep(3)

    # store a new zonefile
    zonefile = blockstack_client.user.make_empty_user_zonefile( "foo.test", data_pubkey )
    blockstack_client.user.put_immutable_data_zonefile( zonefile, "testdata2", blockstack_client.get_data_hash("testdata") )

    zonefile_txt = blockstack_zones.make_zone_file( zonefile )
    zonefile_hash = blockstack_client.storage.get_zonefile_data_hash( zonefile_txt )

    # store locally 
    res = blockstack_client.profile.store_name_zonefile("foo.test", zonefile, None, storage_drivers=['disk'])
    if 'error' in res:
        print >> sys.stderr, "\nFailed to store zonefile: %s\n" % res
        return False

    # update the zonefile hash, but not the zonefile.
    resp = testlib.blockstack_cli_set_zonefile_hash( "foo.test", zonefile_hash )
    if 'error' in resp:
        print >> sys.stderr, "\nFailed to set zonefile hash: %s\n" % resp
        return False

    for i in xrange(0, 12):
        # warn the serialization checker that this changes behavior from 0.13
        print "BLOCKSTACK_SERIALIZATION_CHECK_IGNORE value_hash"
        sys.stdout.flush()
        
        testlib.next_block( **kw )

    # verify that we can sync the zonefile, using the on-disk zonefile
    resp = testlib.blockstack_cli_sync_zonefile( "foo.test" )
    
    if 'error' in resp:
        print >> sys.stderr, "update error: %s" % resp['error']
        return False
    
    # wait for it to go through 
    for i in xrange(0, 12):
        testlib.next_block( **kw )

    print >> sys.stderr, "Waiting 10 seconds for the backend to acknowedge the update"
    time.sleep(10)


def check( state_engine ):

    global zonefile_hash

    # not revealed, but ready 
    ns = state_engine.get_namespace_reveal( "test" )
    if ns is not None:
        print "namespace reveal exists"
        return False 

    ns = state_engine.get_namespace( "test" )
    if ns is None:
        print "no namespace"
        return False 

    if ns['namespace_id'] != 'test':
        print "wrong namespace"
        return False 
    
    # registered 
    name_rec = state_engine.get_name( "foo.test" )
    if name_rec is None:
        print "name does not exist"
        return False 

    # owned by
    owner_address = wallets[3].addr
    if name_rec['address'] != owner_address or name_rec['sender'] != pybitcoin.make_pay_to_address_script(owner_address):
        print "sender is wrong"
        return False 

    # value hash 
    if name_rec['value_hash'] != zonefile_hash:
        print "wrong zonefile hash: %s != %s" % (name_rec['value_hash'], zonefile_hash)
        return False

    # replicated?
    zonefile = testlib.blockstack_get_zonefile( zonefile_hash )
    if 'error' in zonefile:
        print "zonefile error: %s" % zonefile['error']
        return False

    # right hash?
    if blockstack_client.hash_zonefile( zonefile ) != zonefile_hash:
        print "wrong zonefile: %s != %s" % (blockstack_client.hash_zonefile(zonefile), zonefile_hash)
        return False

    # all queues are drained 
    queue_info = testlib.blockstack_client_queue_state()
    if len(queue_info) > 0:
        print "Still in queue:\n%s" % json.dumps(queue_info, indent=4, sort_keys=True)
        return False

    return True
