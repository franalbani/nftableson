#!./venv/bin/python3
from nftables import Nftables
from pprint import pprint
from sys import argv as arguments


family = 'netdev'
table = 'example'
fwd_chain_ac = 'fwd_chain_ac'
fwd_chain_ca = 'fwd_chain_ca'
chain_type = 'filter'
hook = 'ingress'
dev_ba = 'ba_eth'
dev_bc = 'bc_eth'
priority = 1
policy = 'accept'

dev_or_device = 'device'

NFT_CMD = '''
flush ruleset
add table {family} {table}
add chain {family} {table} {fwd_chain_ac} {{ type {chain_type} hook {hook} device {dev_ba} priority {priority}; policy {policy}; }}
add chain {family} {table} {fwd_chain_ca} {{ type {chain_type} hook {hook} device {dev_bc} priority {priority}; policy {policy}; }}
add rule  {family} {table} {fwd_chain_ac} fwd to {dev_bc}
add rule  {family} {table} {fwd_chain_ca} fwd to {dev_ba}
'''.format(family=family,
           table=table,
           fwd_chain_ac=fwd_chain_ac,
           fwd_chain_ca=fwd_chain_ca,
           chain_type=chain_type,
           hook=hook,
           dev_ba=dev_ba,
           dev_bc=dev_bc,
           priority=priority,
           policy=policy,
           )

NFT_CONFIG = {'nftables':
        [
            {'add': {'table':
                {
                    'family': family,
                    'name': table,
                }
            }},
            {'add': {'chain':
                {
                    'family': family,
                    'table': table,
                    'name': fwd_chain_ac,
                    'type': chain_type,
                    'hook': hook,
                    dev_or_device: dev_ba,
                    'priority': priority,
                    'policy': policy,
                }
            }},
            {'add': {'chain':
                {
                    'family': family,
                    'table': table,
                    'name': fwd_chain_ca,
                    'type': chain_type,
                    'hook': hook,
                    dev_or_device: dev_bc,
                    'priority': priority,
                    'policy': policy,
                }
            }},
            {'add': {'rule':
                {
                    'family': family,
                    'table': table,
                    'chain': fwd_chain_ac,
                    'expr': [{'fwd': {'dev': 'bc_eth'}}],
                }
            }},
            {'add': {'rule':
                {
                    'family': family,
                    'table': table,
                    'chain': fwd_chain_ca,
                    'expr': [{'fwd': {'dev': 'ba_eth'}}],
                }
            }},
        ]}


nft = Nftables()
nft.set_json_output(True)

nft.json_validate(NFT_CONFIG)

if len(arguments) != 2:
    raise ValueError('argument must be json_cmd or cmd')

if arguments[1] == 'json_cmd':
    rc, output, error = nft.json_cmd(NFT_CONFIG)
elif 'cmd':
    print(NFT_CMD)
    rc, output, error = nft.cmd(NFT_CMD)
else:
    raise ValueError('argument must be json_cmd or cmd')

if rc != 0:
    print(f'{rc = }')
    print(error)

print('=== nft.json_cmd({"nftables": [{"list": {"ruleset": None}}]}) ===')
_, output, _ = nft.json_cmd({'nftables': [{'list': {'ruleset': None}}]})
pprint(output)
