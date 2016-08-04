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
import json
import shutil
import tempfile
import os
import blockstack_client

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

debug = True
last_consensus = None
snv_block_id_foo = None 
snv_txid_bar = None 

def scenario( wallets, **kw ):

    global snv_block_id_foo, snv_txid_bar, snv_txid_baz, last_consensus 

    # make a test namespace
    resp = testlib.blockstack_namespace_preorder( "test", wallets[1].addr, wallets[0].privkey )
    if debug or 'error' in resp:
        print json.dumps( resp, indent=4 )

    testlib.next_block( **kw )

    resp = testlib.blockstack_namespace_reveal( "test", wallets[1].addr, 52595, 250, 4, [6,5,4,3,2,1,0,0,0,0,0,0,0,0,0,0], 10, 10, wallets[0].privkey )
    if debug or 'error' in resp:
        print json.dumps( resp, indent=4 )

    testlib.next_block( **kw )

    resp = testlib.blockstack_name_import( "foo.test", wallets[3].addr, "11" * 20, wallets[1].privkey )
    if 'error' in resp:
        print json.dumps( resp, indent=4 )

    testlib.next_block( **kw )

    snv_block_id_foo = testlib.get_current_block()

    resp = testlib.blockstack_name_import( "bar.test", wallets[5].addr, "33" * 20, wallets[1].privkey )
    if 'error' in resp:
        print json.dumps( resp, indent=4 )

    testlib.next_block( **kw )

    resp = testlib.blockstack_name_import( "baz.test", wallets[6].addr, "33" * 20, wallets[1].privkey )
    if 'error' in resp:
        print json.dumps( resp, indent=4 )

    testlib.next_block( **kw )

    resp = testlib.blockstack_namespace_ready( "test", wallets[1].privkey )
    if debug or 'error' in resp:
        print json.dumps( resp, indent=4 )

    testlib.next_block( **kw )

    resp = testlib.blockstack_name_transfer( "bar.test", wallets[4].addr, True, wallets[5].privkey )
    if 'error' in resp:
        print json.dumps( resp, indent=4 )

    snv_txid_bar = resp['transaction_hash']
    testlib.next_block( **kw )

    resp = testlib.blockstack_name_update( "baz.test", "22" * 20, wallets[6].privkey )
    if 'error' in resp:
        print json.dumps( resp, indent=4 )

    testlib.next_block( **kw )
    last_consensus = testlib.get_consensus_at( testlib.get_current_block(**kw) )


def check( state_engine ):

    global snv_block_id_foo, snv_txid_bar, last_consensus

    # not revealed, but ready 
    ns = state_engine.get_namespace_reveal( "test" )
    if ns is not None:
        return False 

    ns = state_engine.get_namespace( "test" )
    if ns is None:
        return False 

    if ns['namespace_id'] != 'test':
        return False 

    # not preordered 
    for i in xrange(0, len(wallets)):
        for name in ["foo.test", "bar.test", "baz.test"]:
            preorder = state_engine.get_name_preorder( name, pybitcoin.make_pay_to_address_script(wallets[i].addr), wallets[(i+1)%5].addr )
            if preorder is not None:
                print "preordered"
                return False

    # but still registered 
    for name in ["foo.test", "bar.test", "baz.test"]:
        name_rec = state_engine.get_name( name )
        if name_rec is None:
            print "no name"
            return False 
 
    # updated, and data preserved
    name_rec = state_engine.get_name( "baz.test" )
    if name_rec['value_hash'] != "22" * 20:
        print "wrong value hash"
        return False 

    # transferred 
    name_rec = state_engine.get_name( "bar.test" )
    if name_rec['address'] != wallets[4].addr or name_rec['sender'] != pybitcoin.make_pay_to_address_script( wallets[4].addr ):
        print "wrong owner"
        return False

    # snv lookup works
    # NOTE: cannot use serial numbers here, since a NAME_IMPORT does not contain a consensus hash.
    test_proxy = testlib.TestAPIProxy()
    blockstack_client.set_default_proxy( test_proxy )
    bitcoind = testlib.get_bitcoind()

    snv_rec = blockstack_client.snv_lookup( "foo.test", snv_block_id_foo, last_consensus, proxy=test_proxy ) 
    if 'error' in snv_rec:
        print json.dumps(snv_rec, indent=4 )
        print "failed to look up foo.test from consensus hash %s" % last_consensus
        return False

    # can use bar.test's NAME_TRANSFER txid to verify foo.test, since it has a consensus hash 
    snv_rec_bar_tx = blockstack_client.snv_lookup( "foo.test", snv_block_id_foo, snv_txid_bar, proxy=test_proxy )
    if 'error' in snv_rec_bar_tx:
        print json.dumps( snv_rec_bar_tx, indent=4 )
        print "failed to look up foo.test from transaction %s" % snv_txid_bar
        return False 

    if snv_rec != snv_rec_bar_tx:
        print "--------"
        print json.dumps(snv_rec, indent=4 )
        print ""
        print json.dumps(snv_rec_bar_tx, indent=4 )
        print ""
        print "Not equal"
        return False

    print snv_rec 


    return True
