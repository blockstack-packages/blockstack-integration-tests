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
import blockstack as blockstack_server

wallets = [
    testlib.Wallet( "5JesPiN68qt44Hc2nT8qmyZ1JDwHebfoh9KQ52Lazb1m1LaKNj9", 100000000000 ),
    testlib.Wallet( "5KHqsiU9qa77frZb6hQy9ocV7Sus9RWJcQGYYBJJBb2Efj1o77e", 100000000000 ),
    testlib.Wallet( "5Kg5kJbQHvk1B64rJniEmgbD83FpZpbw2RjdAZEzTefs9ihN3Bz", 100000000000 ),
    testlib.Wallet( "5JuVsoS9NauksSkqEjbUZxWwgGDQbMwPsEfoRBSpLpgDX1RtLX7", 100000000000 ),
    testlib.Wallet( "5KEpiSRr1BrT8vRD7LKGCEmudokTh1iMHbiThMQpLdwBwhDJB1T", 100000000000 ),
    testlib.Wallet( "5K5hDuynZ6EQrZ4efrchCwy6DLhdsEzuJtTDAf3hqdsCKbxfoeD", 100000000000 ),
    testlib.Wallet( "5J39aXEeHh9LwfQ4Gy5Vieo7sbqiUMBXkPH7SaMHixJhSSBpAqz", 100000000000 ),
    testlib.Wallet( "5K9LmMQskQ9jP1p7dyieLDAeB6vsAj4GK8dmGNJAXS1qHDqnWhP", 100000000000 ),
    testlib.Wallet( "5KcNen67ERBuvz2f649t9F2o1ddTjC5pVUEqcMtbxNgHqgxG2gZ", 100000000000 ),
    testlib.Wallet( "5Jyq6RH7H42aPasyrvobvLvZGPDGYrq9m2Gq5qPEkAwDD7fqNHu", 100000000000 ),
    testlib.Wallet( "5KBc5xk9Rk3qmYg1PXPzsJ1kPfJkvzShK5ZGEn3q4Gzw4JWqMuy", 100000000000 ),
    testlib.Wallet( "5K6Nou64uUXg8YzuiVuRQswuGRfH1tdb9GUC9NBEV1xmKxWMJ54", 100000000000 )
]

consensus = "17ac43c1d8549c3181b200f1bf97eb7d"

transfer_blocks = []
update_blocks = []

transfer_recipients = []
update_hashes = []


def scenario( wallets, **kw ):

    global update_blocks, transfer_blocks, update_hashes, transfer_recipients
    
    testlib.blockstack_namespace_preorder( "test", wallets[1].addr, wallets[0].privkey )
    testlib.next_block( **kw )

    testlib.blockstack_namespace_reveal( "test", wallets[1].addr, 2, 250, 4, [6,5,4,3,2,1,0,0,0,0,0,0,0,0,0,0], 10, 10, wallets[0].privkey )
    testlib.next_block( **kw )

    testlib.blockstack_namespace_ready( "test", wallets[1].privkey )
    testlib.next_block( **kw )

    # preorder, register, update, expire (multiple times)
    for i in xrange(2, 11):
        resp = testlib.blockstack_name_preorder( "foo.test", wallets[i].privkey, wallets[(i+1)%11].addr )
        if 'error' in resp:
            print json.dumps( resp, indent=4 )

        testlib.next_block( **kw )
   
        resp = testlib.blockstack_name_register( "foo.test", wallets[i].privkey, wallets[(i+1)%11].addr )
        if 'error' in resp:
            print json.dumps( resp, indent=4 )

        testlib.next_block( **kw )

        resp = testlib.blockstack_name_update( "foo.test", ("%02x" % i) * 20, wallets[(i+1)%11].privkey )
        if 'error' in resp:
            print json.dumps( resp, indent=4 )

        testlib.next_block( **kw )

        update_blocks.append( testlib.get_current_block( **kw )) 
        update_hashes.append( ("%02x" % i) * 20 )

        resp = testlib.blockstack_name_transfer( "foo.test", wallets[i].addr, True, wallets[(i+1)%11].privkey )
        if 'error' in resp:
            print json.dumps( resp, indent=4 )

        testlib.next_block( **kw )
         
        transfer_blocks.append( testlib.get_current_block( **kw ) )
        transfer_recipients.append( wallets[i].addr )

        if i == 10:
            break

        for j in xrange(0, 2 * blockstack_server.NAMESPACE_LIFETIME_MULTIPLIER - 1):
            testlib.next_block( **kw )


def check( state_engine ):
    
    global update_blocks, transfer_blocks, update_hashes, transfer_recipients

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
    preorder = state_engine.get_name_preorder( "foo.test", pybitcoin.make_pay_to_address_script(wallets[2].addr), wallets[3].addr )
    if preorder is not None:
        print json.dumps(name_rec, indent=4)
        return False
    
    # registered to new owner
    name_rec = state_engine.get_name( "foo.test" )
    if name_rec is None:
        print "name rec is None"
        return False 

    # updated 
    if name_rec['value_hash'] != '0a' * 20:
        print "invalid value hash"
        return False 

    # transferred
    if name_rec['address'] != wallets[10].addr or name_rec['sender'] != pybitcoin.make_pay_to_address_script(wallets[10].addr):
        print json.dumps(name_rec, indent=4 )
        return False

    # historically updated and transferred 
    if len(transfer_blocks) != len(update_blocks):
        print "test bug: did not transfer or update the right amount of times"
        return False

    for i in xrange(0, len(transfer_blocks)):
        transfer_block = transfer_blocks[i]
        transfer_recipient = transfer_recipients[i]

        historic_name_rec = state_engine.get_name_at( "foo.test", transfer_block, include_expired=True )
        if historic_name_rec is None or len(historic_name_rec) == 0:
            print "no name at %s" % transfer_block
            return False

        historic_name_rec = historic_name_rec[0]
        if historic_name_rec['opcode'] != 'NAME_TRANSFER':
            print "was not transfered at %s" % transfer_block
            return False

        if historic_name_rec['address'] != transfer_recipient or historic_name_rec['sender'] != pybitcoin.make_pay_to_address_script(transfer_recipient):
            print "wrong address/sender, got %s, %s" % (historic_name_rec['address'], historic_name_rec['sender'])
            return False

    for i in xrange(0, len(update_blocks)):
        update_block = update_blocks[i]
        update_hash = update_hashes[i]

        historic_name_rec = state_engine.get_name_at( "foo.test", update_block, include_expired=True )
        if historic_name_rec is None or len(historic_name_rec) == 0:
            print "No name at %s" % update_block
            return False

        historic_name_rec = historic_name_rec[0]
        if historic_name_rec['opcode'] != 'NAME_UPDATE':
            print "was not updated at %s" % update_block
            return False

        if historic_name_rec.get('value_hash', None) != update_hash:
            print "wrong update hash: expected %s, got %s" % (update_hash, historic_name_rec.get('value_hash', None))
            return False

    return True
