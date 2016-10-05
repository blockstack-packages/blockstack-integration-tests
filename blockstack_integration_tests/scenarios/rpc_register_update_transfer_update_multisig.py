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
import virtualchain
import blockstack_client

# activate multisig
"""
TEST ENV BLOCKSTACK_EPOCH_1_END_BLOCK 250
TEST ENV BLOCKSTACK_EPOCH_2_NAMESPACE_LIFETIME_MULTIPLIER 1
"""

wallets = [
    testlib.Wallet( "5JesPiN68qt44Hc2nT8qmyZ1JDwHebfoh9KQ52Lazb1m1LaKNj9", 100000000000 ),
    testlib.Wallet( "5KHqsiU9qa77frZb6hQy9ocV7Sus9RWJcQGYYBJJBb2Efj1o77e", 100000000000 ),
    testlib.MultisigWallet(2, "5JfHdMq9XnZ9mwW5H6LsfVCn9u6iGAj2FCVYtfhcHn72Tphvm5P", "5JaqLZaKD7cgkfsxSZBNiu6gaFxo1XAiTXw1mhtatipNNCtZBZG", "5KNsAkiHRDZb5Yyedxov2Fncr6CcNPV52yqJbzQ8M2W6dkg2qJp"),
    testlib.MultisigWallet(2, "5JPrkpfLT3rDf1Lgm1DpA2Cfepwf9wCtEbDx1HSEdd4J2R5YMxZ", "5JiALcfvzFsKcvLnHf7ECgLdp6FxbcAXB1GPvEYP7HeigbDCQ9E", "5KScD5XL5Hj83Yjvm3u4HD78vSYwFRyq9StTLPnrWrCTGiqTvVP"),
    testlib.MultisigWallet(2, '5JpAkdEJuzF8E74UptksRLiB6Bf9QnwxGQutJTRWo5EAGVZfXmY', '5Hyc4wreVpZyzcfb56Zt1ymovda2xGucGZsAwoQz34iYK6aEKhR', '5JypKiQGiaD8AN6X86xtnuQYj7nnpLvp4VfcTVdDh4yFkLewAGx'),
    testlib.Wallet( "5Kg5kJbQHvk1B64rJniEmgbD83FpZpbw2RjdAZEzTefs9ihN3Bz", 100000000000 ),
    testlib.Wallet( "5JuVsoS9NauksSkqEjbUZxWwgGDQbMwPsEfoRBSpLpgDX1RtLX7", 100000000000 ),
    testlib.Wallet( "5KEpiSRr1BrT8vRD7LKGCEmudokTh1iMHbiThMQpLdwBwhDJB1T", 100000000000 ),
    testlib.Wallet( "5K6TSyEeEAeDynw8R2imSwebp9An2Vjnd4q5o8GmKWJLbQ2i9Rp", 100000000000 )
]

consensus = "17ac43c1d8549c3181b200f1bf97eb7d"
zonefile_hash = None
new_data_pubkey = '048d1b05b569b706692bde5a85762e84f452660867687cbbe7443719475eaaf5817e2de389e43befdbe14d90987fda7062d115e21a787fcb39a654be65012bf4ea'

def scenario( wallets, **kw ):

    global zonefile_hash

    testlib.blockstack_namespace_preorder( "test", wallets[1].addr, wallets[0].privkey )
    testlib.next_block( **kw )

    testlib.blockstack_namespace_reveal( "test", wallets[1].addr, 52595, 250, 4, [6,5,4,3,2,1,0,0,0,0,0,0,0,0,0,0], 10, 10, wallets[0].privkey )
    testlib.next_block( **kw )

    testlib.blockstack_namespace_ready( "test", wallets[1].privkey )
    testlib.next_block( **kw )

    wallet = testlib.blockstack_client_initialize_wallet( "0123456789abcdef", wallets[2].privkey, wallets[3].privkey, wallets[5].privkey )
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

    # wait for update to get confirmed 
    for i in xrange(0, 12):
        # warn the serialization checker that this changes behavior from 0.13
        print "BLOCKSTACK_SERIALIZATION_CHECK_IGNORE value_hash"
        sys.stdout.flush()
        
        testlib.next_block( **kw )

    print >> sys.stderr, "Waiting 10 seconds for the backend to acknowledge update"
    time.sleep(10)

    # send an update, changing the zonefile
    data_pubkey = wallet['data_pubkey']
    zonefile = blockstack_client.user.make_empty_user_zonefile( "foo.test", data_pubkey )
    blockstack_client.user.put_immutable_data_zonefile( zonefile, "testdata", blockstack_client.get_data_hash("testdata"), data_url="file:///testdata")
    zonefile_json = json.dumps(zonefile)

    resp = testlib.blockstack_cli_update( "foo.test", zonefile_json, "0123456789abcdef" )
    
    if 'error' in resp:
        print >> sys.stderr, "update error: %s" % resp['error']
        return False

    zonefile_hash = resp['value_hash']
    
    # wait for it to go through 
    for i in xrange(0, 12):
        # warn the serialization checker that this changes behavior from 0.13
        print "BLOCKSTACK_SERIALIZATION_CHECK_IGNORE value_hash"
        sys.stdout.flush()
        
        testlib.next_block( **kw )

    print >> sys.stderr, "Waiting 10 seconds for the backend to acknowedge the update"
    time.sleep(10)

    # transfer to a new address 
    resp = testlib.blockstack_cli_transfer( "foo.test", wallets[4].addr, "0123456789abcdef" )

    if 'error' in resp:
        print >> sys.stderr, "transfer error: %s" % resp['error']
        return False

    # wait for it to go through 
    for i in xrange(0, 12):
        # warn the serialization checker that this changes behavior from 0.13
        print "BLOCKSTACK_SERIALIZATION_CHECK_IGNORE value_hash"
        sys.stdout.flush()
        
        testlib.next_block( **kw )

    print >> sys.stderr, "Waiting 10 seconds for the backend to acknowledge the transfer"
    time.sleep(10)

    # regenerate the wallet, with the new owner address
    wallet = testlib.blockstack_client_set_wallet( "0123456789abcdef", wallets[5].privkey, wallets[4].privkey, wallets[5].privkey )

    # send another update, changing the zonefile again
    # pay for it using the same payment address
    zonefile = blockstack_client.user.make_empty_user_zonefile( "foo.test", new_data_pubkey )
    blockstack_client.user.put_immutable_data_zonefile( zonefile, "testdata", blockstack_client.get_data_hash("testdata"), data_url="file:///testdata")
    zonefile_json = json.dumps(zonefile)

    resp = testlib.blockstack_cli_update( "foo.test", zonefile_json, "0123456789abcdef" )
    
    if 'error' in resp:
        print >> sys.stderr, "update error: %s" % resp['error']
        return False

    zonefile_hash = resp['value_hash']
    
    # wait for it to go through 
    for i in xrange(0, 12):
        # warn the serialization checker that this changes behavior from 0.13
        print "BLOCKSTACK_SERIALIZATION_CHECK_IGNORE value_hash"
        sys.stdout.flush()
        
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
    owner_address = wallets[4].addr
    if name_rec['address'] != owner_address or name_rec['sender'] != virtualchain.make_payment_script(owner_address):
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

    # latest key?
    if not zonefile.has_key("txt"):
        print "no txt:\n%s" % json.dumps(zonefile, indent=4, sort_keys=True)
        return False 

    if len(zonefile['txt']) != 2:
        print "wrong number of txt records:\n%s" % json.dumps(zonefile, indent=4, sort_keys=True)
        return False

    for txtrec in zonefile['txt']:
        if txtrec['name'] == 'pubkey':
            if new_data_pubkey not in txtrec['txt']:
                print "wrong pubkey:\n%s" % json.dumps(zonefile, indent=4, sort_keys=True)
                print "missing %s" % new_data_pubkey
                return False

    names_owned = testlib.blockstack_cli_names()
    if 'error' in names_owned:
        print "rpc names: %s" % names_owned['error']
        return False

    # we still own the name
    if len(names_owned['names_owned']) != 1:
        print "owned: %s" % names_owned['names_owned']
        return False

    # all queues are drained 
    queue_info = testlib.blockstack_client_queue_state()
    if len(queue_info) > 0:
        print "Still in queue:\n%s" % json.dumps(queue_info, indent=4, sort_keys=True)
        return False

    return True
