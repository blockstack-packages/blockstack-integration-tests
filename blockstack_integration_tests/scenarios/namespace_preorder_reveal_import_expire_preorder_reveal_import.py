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

# test framework pragmas
"""
TEST ENV BLOCKSTACK_NAMESPACE_REVEAL_EXPIRE 3
"""

import os
import testlib 
import json
import pybitcoin

wallets = [
    testlib.Wallet( "5JesPiN68qt44Hc2nT8qmyZ1JDwHebfoh9KQ52Lazb1m1LaKNj9", 100000000000 ),
    testlib.Wallet( "5KHqsiU9qa77frZb6hQy9ocV7Sus9RWJcQGYYBJJBb2Efj1o77e", 100000000000 ),
    testlib.Wallet( "5Kg5kJbQHvk1B64rJniEmgbD83FpZpbw2RjdAZEzTefs9ihN3Bz", 100000000000 ),
    testlib.Wallet( "5JuVsoS9NauksSkqEjbUZxWwgGDQbMwPsEfoRBSpLpgDX1RtLX7", 100000000000 ),
    testlib.Wallet( "5KEpiSRr1BrT8vRD7LKGCEmudokTh1iMHbiThMQpLdwBwhDJB1T", 100000000000 ),
    testlib.Wallet( "5K5hDuynZ6EQrZ4efrchCwy6DLhdsEzuJtTDAf3hqdsCKbxfoeD", 100000000000 ),
    testlib.Wallet( "5J39aXEeHh9LwfQ4Gy5Vieo7sbqiUMBXkPH7SaMHixJhSSBpAqz", 100000000000 ),
    testlib.Wallet( "5K9LmMQskQ9jP1p7dyieLDAeB6vsAj4GK8dmGNJAXS1qHDqnWhP", 100000000000 )
]

reveal_block = None
first_registered_block = None
consensus = "17ac43c1d8549c3181b200f1bf97eb7d"
namespace_block_number = None

def scenario( wallets, **kw ): 

    global reveal_block, namespace_block_number, first_registered_block

    resp = testlib.blockstack_namespace_preorder( "test", wallets[1].addr, wallets[0].privkey )
    if 'error' in resp:
        print json.dumps(resp, indent=4)

    testlib.next_block( **kw )
    namespace_block_number = testlib.get_current_block(**kw)

    # reveal it  
    testlib.blockstack_namespace_reveal( "test", wallets[1].addr, 52595, 250, 4, [6,5,4,3,2,1,0,0,0,0,0,0,0,0,0,0], 10, 10, wallets[0].privkey )
    testlib.next_block( **kw )

    # import some names
    testlib.blockstack_name_import( "foo.test", wallets[2].addr, "11" * 20, wallets[1].privkey )
    testlib.blockstack_name_import( "bar.test", wallets[3].addr, "22" * 20, wallets[1].privkey )
    testlib.blockstack_name_import( "baz.test", wallets[4].addr, "33" * 20, wallets[1].privkey )
    testlib.next_block( **kw )
    first_registered_block = testlib.get_current_block(**kw)

    # expire it (3 blocks later)
    for i in xrange(0, 3): 
        testlib.next_block( **kw )

    # try to ready it (should fail)
    resp = testlib.blockstack_namespace_ready( "test", wallets[1].privkey )
    if 'error' in resp:
        print json.dumps(resp, indent=4)

    testlib.next_block( **kw )

    # try to re-preorder it 
    resp = testlib.blockstack_namespace_preorder( "test", wallets[3].addr, wallets[2].privkey )
    if 'error' in resp:
        print json.dumps(resp, indent=4)

    testlib.next_block( **kw )

    # try to re-reveal it 
    testlib.blockstack_namespace_reveal( "test", wallets[3].addr, 52595, 250, 4, [6,5,4,3,2,1,0,0,0,0,0,0,0,0,0,0], 10, 10, wallets[2].privkey )
    testlib.next_block( **kw )
    reveal_block = testlib.get_current_block(**kw) 

    # import some names
    testlib.blockstack_name_import( "foo.test", wallets[2].addr, "11" * 20, wallets[1].privkey )
    testlib.blockstack_name_import( "bar.test", wallets[3].addr, "22" * 20, wallets[1].privkey )
    testlib.blockstack_name_import( "baz.test", wallets[4].addr, "33" * 20, wallets[1].privkey )
    testlib.next_block( **kw )



def check( state_engine ):

    global reveal_block, namespace_block_number
    
    # the namespace should not exist
    ns = state_engine.get_namespace_reveal( "test" )
    if ns is None:
        print "not revealed"
        return False 
    
    # should not be preordered
    namespace_preorder_hashes = state_engine.get_all_preordered_namespace_hashes()
    if len(namespace_preorder_hashes) != 0:
        print "preorder hashes: %s" % namespace_preorder_hashes
        return False 

    # should be revealed at the right block
    if ns['reveal_block'] != reveal_block:
        print "revealed at %s, but expected %s" % (ns['reveal_block'], reveal_block)
        return False 

    # should be revealed by wallets[1]
    if ns['sender'] != pybitcoin.make_pay_to_address_script( wallets[2].addr ):
        print "not sent by '%s'" % ns['sender'] 
        return False

    # names should exist, and be sent by wallets[1]
    for name in ['foo.test', 'bar.test', 'baz.test']:
        name_rec = state_engine.get_name( name )
        if name_rec is None:
            print "name '%s' does not exist" % name
            return False 

        if name_rec['first_registered'] != first_registered_block:
            print "name '%s' first_registered at %s; expected %s" % (name, name_rec['first_registered'], first_registered_block )
            return False 

        if name_rec['last_renewed'] != first_registered_block:
            print "name '%s' last_renewed at %s; expected %s" % (name, name_rec['last_renewed'], first_registered_block )
            return False

        if name_rec['namespace_block_number'] != namespace_block_number:
            print "name '%s' namespace_block_number = %s (expected %s) " % (name, name_rec['namespace_block_number'], namespace_block_number)
            return False


    return True

