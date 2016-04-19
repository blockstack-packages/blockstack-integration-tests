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

wallets = [
    testlib.Wallet( "5JesPiN68qt44Hc2nT8qmyZ1JDwHebfoh9KQ52Lazb1m1LaKNj9", 100000000000 ),
    testlib.Wallet( "5KHqsiU9qa77frZb6hQy9ocV7Sus9RWJcQGYYBJJBb2Efj1o77e", 100000000000 )
]

consensus = "17ac43c1d8549c3181b200f1bf97eb7d"
preorder_block = None
reveal_block = None

def scenario( wallets, **kw ):

    global reveal_block
    global preorder_block 

    testlib.blockstack_namespace_preorder( "test", wallets[1].addr, wallets[0].privkey )
    preorder_block = testlib.get_current_block( **kw ) + 1
    testlib.next_block( **kw )
    
    testlib.blockstack_namespace_reveal( "test", wallets[1].addr, 52595, 250, 4, [6,5,4,3,2,1,0,0,0,0,0,0,0,0,0,0], 10, 10, wallets[0].privkey )
    reveal_block = testlib.get_current_block( **kw ) + 1

    testlib.next_block( **kw )

def check( state_engine ):

    global reveal_block, preorder_block

    # the namespace has to have been revealed 
    ns = state_engine.get_namespace_reveal( "test" )
    if ns is None:
        return False 

    if ns["namespace_id"] != "test":
        print "wrong namespace ID"
        return False 

    if ns["lifetime"] != 52595:
        print "wrong lifetime"
        return False 

    if ns["coeff"] != 250:
        print "wrong coeff"
        return False 

    if ns["base"] != 4:
        print "wrong base"
        return False 

    if ns["buckets"] != [6,5,4,3,2,1,0,0,0,0,0,0,0,0,0,0]:
        print "wrong buckets"
        return False 

    if ns["no_vowel_discount"] != 10:
        print "wrong no-vowel discount"
        return False

    if ns["nonalpha_discount"] != 10:
        print "wrong nonalpha discount"
        return False

    if ns["reveal_block"] != reveal_block:
        print "wrong reveal block (%s)" % reveal_block
        return False 

    if ns["block_number"] != preorder_block:
        print "wrong block number"
        return False 

    return True
