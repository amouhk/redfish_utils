import datetime
import getopt
import logging
import os
import sys
import time
import traceback

from tools.mesca3.redfish_utils.BootOption import BootOption


def usage():
    print('\n' + __file__ + 'usage:')
    print('  -h   display usage and exit')
    print('  -u   user name,                                     default Administrator')
    print('  -p   password,                                      default Administrator ')
    print('  -H   IP address,                                    default 172.31.100.156')
    print('  -M   Module Id,                                     default x')
    print('  -a   Action (set | get),                            default: get')
    print('  -d   Boot from device (None|Pxe|Disk|Diag|Bios)     default None')
    print('  -i   selected instance number ( 0 - 15 )            default 0 ')
    print('  -c   clear cmos,                                    default no')
    print('  -r   keep changes,                                  default no ')
    print('  -v   Verbose (N|Y),                                 Versbose')
    print('\n')
    sys.exit()


obj_boot_option = BootOption()

module_id = 9999
action = "list"
action_step = "all"
verbose = ""
# parse args
try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "h:u:p:H:M:a:d:i:c:r:v:")
    for opt, arg in opts:
        if opt in '-h':
            usage()
        elif opt in '-u':
            obj_boot_option.username = arg
        elif opt in '-p':
            obj_boot_option.password = arg
        elif opt in '-H':
            obj_boot_option.bmc_ip = arg
        elif opt in '-M':
            module_id = int(arg)
        elif opt in '-a':
            action = arg
        elif opt in '-d':
            obj_boot_option.set_device(arg)
        elif opt in '-i':
            obj_boot_option.set_instance(arg)
        elif opt in '-c':
            obj_boot_option.set_clr_cmos(arg)
        elif opt in '-r':
            obj_boot_option.set_persistant(arg)
        elif opt in '-v':
            verbose = arg

except getopt.GetoptError:
    print("Error parsing options")
    usage()
except Exception:
    traceback.print_exc()
    usage()

# obj_boot_option

if action == "set":
    obj_boot_option.print_option()
    obj_boot_option.apply_option()

else:
    print("get action ")