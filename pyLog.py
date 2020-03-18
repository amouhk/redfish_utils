import getopt
import os
import pprint
import sys
import traceback
import xml.etree.ElementTree as xml

from BMCInfo import BMCInfo


def usage():
    print('\n' + __file__ + ' usage:')
    print('  -h   display usage and exit')
    print('  -u   user name,                                              default Administrator')
    print('  -p   password,                                               default Administrator ')
    print('  -H   IP address,                                             default 172.31.100.156')
    print('  -M   Module Id,                                              default x')
    print('  -a   Action (clear_log|),                                    default: list')
    print('  -D   Technical state dir,                                    default: ')
    print('  -v   Verbose (N|Y),                                          Versbose')
    print('\n')
    sys.exit()

def clear_logs():



obj_bmc = BMCInfo()
module_id = 9999
action = ""
verbose = ""
# parse args
try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "h:u:p:H:M:a:s:F:E:v:")
    for opt, arg in opts:
        if opt in '-h':
            usage()
        elif opt in '-u':
            obj_bmc.username = arg
        elif opt in '-p':
            obj_bmc.password = arg
        elif opt in '-H':
            obj_bmc.bmc_ip = arg
        elif opt in '-M':
            module_id = int(arg)
        elif opt in '-a':
            action = arg
        elif opt in '-v':
            verbose = arg
except getopt.GetoptError:
    print("Error parsing options")
    usage()
except Exception:
    traceback.print_exc()
    usage()


