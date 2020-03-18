import datetime
import getopt
import logging
import os
import sys
import time
import traceback

import requests
from tools.mesca3.redfish_utils.PowerAction import PowerAction


def usage():
    print('\n' + __file__ + ' usage:')
    print('  -h   display usage and exit')
    print('  -u   user name,                                              default Administrator')
    print('  -p   password,                                               default Administrator ')
    print('  -H   IP address,                                             default 172.31.100.156')
    print('  -M   Module Id,                                              default x')
    print('  -a   Action ( on | off | off_force | power_cycle | BMCreset) default: list')
    print('  -v   Verbose (N|Y),                                          Versbose')
    print('\n')
    sys.exit()


obj_power = PowerAction()

module_id = 9999
action = "list"
action_step = "all"
verbose = ""
# parse args
try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "h:u:p:H:M:a:v:")
    for opt, arg in opts:
        if opt in '-h':
            usage()
        elif opt in '-u':
            obj_power.username = arg
        elif opt in '-p':
            obj_power.password = arg
        elif opt in '-H':
            obj_power.bmc_ip = arg
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

try:
    os.makedirs("/var/log/redfish/", exist_ok=True)
    log_file = "/var/log/redfish/" + __file__ + "_" + obj_power.bmc_ip + "_" + action + "_" \
               + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".log"
    obj_power.set_log(log_file)

    logging.info(__file__)

    if action == "BMCreset":
        if module_id == 9999:
            obj_power.reset_all()
        else:
            obj_power.reset_module(module_id)

        obj_power.wait_mc_available()

    elif action == "status":
        obj_power.status()
        print("Server is {st}".format(st=obj_power.power_state))

    elif action == "off_force":
        obj_power.force_off()

    elif action == "on":
        obj_power.on()

    elif action == "off":
        obj_power.graceful_shutdown()

    elif action == "power_cycle":
        obj_power.force_cycle()

    else:
        print("No action mentionned")
        usage()

except requests.exceptions.InvalidURL:
    traceback.print_exc()
    logging.exception(repr(traceback.extract_stack()))
    usage()
except requests.exceptions.ConnectionError:
    print("Connection impossible unknown BMC IP address ....")
    traceback.print_exc()
    logging.exception(repr(traceback.extract_stack()))
    usage()
except Exception:
    traceback.print_exc()
    logging.exception(repr(traceback.extract_stack()))
    usage()
except KeyboardInterrupt:
    print("Program interrupt by user ")
