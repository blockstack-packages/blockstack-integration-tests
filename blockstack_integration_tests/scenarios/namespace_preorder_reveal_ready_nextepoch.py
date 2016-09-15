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

"""
TEST ENV BLOCKSTACK_EPOCH_1_END_BLOCK 258
"""

import testlib
import pybitcoin
import json
import shutil
import tempfile

import blockstack

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

def scenario( wallets, **kw ):

    testlib.blockstack_namespace_preorder( "t", wallets[1].addr, wallets[0].privkey )
    testlib.blockstack_namespace_preorder( "te", wallets[2].addr, wallets[1].privkey )
    testlib.blockstack_namespace_preorder( "test", wallets[3].addr, wallets[2].privkey )
    testlib.blockstack_namespace_preorder( "testtest", wallets[4].addr, wallets[3].privkey )

    testlib.next_block( **kw )

    testlib.blockstack_namespace_reveal( "t", wallets[1].addr, 52595, 250, 4, [6,5,4,3,2,1,0,0,0,0,0,0,0,0,0,0], 10, 10, wallets[0].privkey )
    testlib.blockstack_namespace_reveal( "te", wallets[2].addr, 52595, 250, 4, [6,5,4,3,2,1,0,0,0,0,0,0,0,0,0,0], 10, 10, wallets[1].privkey )
    testlib.blockstack_namespace_reveal( "test", wallets[3].addr, 52595, 250, 4, [6,5,4,3,2,1,0,0,0,0,0,0,0,0,0,0], 10, 10, wallets[2].privkey )
    testlib.blockstack_namespace_reveal( "testtest", wallets[4].addr, 52595, 250, 4, [6,5,4,3,2,1,0,0,0,0,0,0,0,0,0,0], 10, 10, wallets[3].privkey )

    testlib.next_block( **kw )

    testlib.blockstack_namespace_ready( "t", wallets[1].privkey )
    testlib.blockstack_namespace_ready( "te", wallets[2].privkey )
    testlib.blockstack_namespace_ready( "test", wallets[3].privkey )
    testlib.blockstack_namespace_ready( "testtest", wallets[4].privkey )

    testlib.next_block( **kw )

    # next epoch 
    
    testlib.blockstack_namespace_preorder( "a", wallets[1].addr, wallets[5].privkey )
    testlib.blockstack_namespace_preorder( "as", wallets[2].addr, wallets[6].privkey )
    testlib.blockstack_namespace_preorder( "asdf", wallets[3].addr, wallets[7].privkey )
    testlib.blockstack_namespace_preorder( "asdfasdf", wallets[4].addr, wallets[8].privkey )

    testlib.next_block( **kw )

    testlib.blockstack_namespace_reveal( "a", wallets[1].addr, 52595, 250, 4, [6,5,4,3,2,1,0,0,0,0,0,0,0,0,0,0], 10, 10, wallets[5].privkey )
    testlib.blockstack_namespace_reveal( "as", wallets[2].addr, 52595, 250, 4, [6,5,4,3,2,1,0,0,0,0,0,0,0,0,0,0], 10, 10, wallets[6].privkey )
    testlib.blockstack_namespace_reveal( "asdf", wallets[3].addr, 52595, 250, 4, [6,5,4,3,2,1,0,0,0,0,0,0,0,0,0,0], 10, 10, wallets[7].privkey )
    testlib.blockstack_namespace_reveal( "asdfasdf", wallets[4].addr, 52595, 250, 4, [6,5,4,3,2,1,0,0,0,0,0,0,0,0,0,0], 10, 10, wallets[8].privkey )

    testlib.next_block( **kw )

    testlib.blockstack_namespace_ready( "a", wallets[1].privkey )
    testlib.blockstack_namespace_ready( "as", wallets[2].privkey )
    testlib.blockstack_namespace_ready( "asdf", wallets[3].privkey )
    testlib.blockstack_namespace_ready( "asdfasdf", wallets[4].privkey )

    testlib.next_block( **kw )



def check( state_engine ):

    fees = {
        "t": blockstack.NAMESPACE_1_CHAR_COST * blockstack.config.EPOCHS[0]['PRICE_MULTIPLIER'],
        "te": blockstack.NAMESPACE_23_CHAR_COST * blockstack.config.EPOCHS[0]['PRICE_MULTIPLIER'],
        "test": blockstack.NAMESPACE_4567_CHAR_COST * blockstack.config.EPOCHS[0]['PRICE_MULTIPLIER'],
        "testtest": blockstack.NAMESPACE_8UP_CHAR_COST * blockstack.config.EPOCHS[0]['PRICE_MULTIPLIER'],

        "a": blockstack.NAMESPACE_1_CHAR_COST * blockstack.config.EPOCHS[1]['PRICE_MULTIPLIER'],
        "as": blockstack.NAMESPACE_23_CHAR_COST * blockstack.config.EPOCHS[1]['PRICE_MULTIPLIER'],
        "asdf": blockstack.NAMESPACE_4567_CHAR_COST * blockstack.config.EPOCHS[1]['PRICE_MULTIPLIER'],
        "asdfasdf": blockstack.NAMESPACE_8UP_CHAR_COST * blockstack.config.EPOCHS[1]['PRICE_MULTIPLIER']
    }

    # not revealed, but ready 
    for nsid in fees.keys():
        ns = state_engine.get_namespace_reveal( nsid )
        if ns is not None:
            return False 

        ns = state_engine.get_namespace( nsid )
        if ns is None:
            return False 

        if ns['namespace_id'] != nsid:
            return False 

        if abs(ns['op_fee'] - fees[nsid]) >= 10e-8:
            print "invalid fee: %s = %s (expected %s)" % (nsid, ns['op_fee'], fees[nsid])
            return False

    return True
