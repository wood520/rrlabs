#!/usr/bin/env python3
""" Create Interface Policies """
__author__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__copyright__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__license__ = 'https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode'
__revision__ = '20180320'

import getopt, logging, json, requests, sys, urllib3
from login_aci import *
urllib3.disable_warnings()

# Reading options
username = None
password = None
apic_host = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'du:p:h:')
except getopt.GetoptError as err:
    logging.error(err)
    usage()
    sys.exit(255)
for opt, arg in opts:
    if opt == '-d':
        logging.basicConfig(level = logging.DEBUG)
    elif opt == '-u':
        username = arg
    elif opt == '-p':
        password = arg
    elif opt == '-h':
        apic_host = arg
    else:
        assert False, 'unhandled option'

# Checking options
if username == None:
    logging.error('username not set')
    usage()
    sys.exit(255)
if password == None:
    logging.error('password not set')
    usage()
    sys.exit(255)
if apic_host == None:
    logging.error('APIC not set')
    usage()
    sys.exit(255)

login_url = 'https://{}/api/aaaLogin.json?gui-token-request=yes'.format(apic_host)

token, cookies, response_code = login(url = login_url, username = username, password = password)

if response_code != 200:
    logging.error('failed to login')
    sys.exit(1)

policies = {
	"CDP": {
		"cdpIfPol": {
			"attributes": {
				"adminSt": "enabled",
				"descr": "Enable CDP protocol.",
				"dn": "uni/infra/cdpIfP-CDP_on"
			}
		}
	},
	"LLDP": {
		"lldpIfPol": {
			"attributes": {
				"adminRxSt": "enabled",
				"adminTxSt": "enabled",
				"descr": "Enable LLDP protocol.",
				"dn": "uni/infra/lldpIfP-LLDP_on"
			}
		}
	},
	"LACP_active": {
		"lacpLagPol": {
			"attributes": {
				"ctrl": "fast-sel-hot-stdby,graceful-conv,susp-individual",
				"descr": "Port-Channel with LACP in active mode.",
				"dn": "uni/infra/lacplagp-PC_LACP",
				"maxLinks": "16",
				"minLinks": "1",
				"mode": "active"
			}
		}
	},
	"LACP_active_no_suspend": {
		"lacpLagPol": {
			"attributes": {
				"ctrl": "fast-sel-hot-stdby,graceful-conv",
				"descr": "Port-Channel with LACP in active mode. Individual interfaces are not suspended.",
				"dn": "uni/infra/lacplagp-PC_LACP_no_suspend",
				"maxLinks": "16",
				"minLinks": "1",
				"mode": "off"
			}
		}
	},
	"LACP_static": {
		"lacpLagPol": {
			"attributes": {
				"ctrl": "fast-sel-hot-stdby,graceful-conv,susp-individual",
				"descr": "Static Port-Channel.",
				"dn": "uni/infra/lacplagp-PC_static",
				"maxLinks": "16",
				"minLinks": "1",
				"mode": "off"
			}
		}
	},
	"BPDU_guard": {
		"stpIfPol": {
			"attributes": {
				"ctrl": "bpdu-guard",
				"descr": "Shutdown if receiving BPDU.",
				"dn": "uni/infra/ifPol-BPDU_guard"
			}
		}
	},
	"BPDU_filter": {
		"stpIfPol": {
			"attributes": {
				"ctrl": "bpdu-filter",
				"descr": "Filter incoming BPDU.",
				"dn": "uni/infra/ifPol-BPDU_filter"
			}
		}
	}
}

url = 'https://{}/api/mo/uni.json?challenge={}'.format(apic_host, token)

for policy_name in policies:
    r = requests.post(url, verify = False, cookies = cookies, data = json.dumps(policies[policy_name]))
    response = r.json()
    response_code = r.status_code
    if response_code != 200:
        logging.error('failed to add interface policy "{}"'.format(policy_name))