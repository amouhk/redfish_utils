import argparse
import datetime
import logging
import os
import sys
import traceback
import requests
from PowerAction import PowerAction

obj_power = PowerAction()
log_file = ""

try:
    power_action_values = ["status, on, off, off_force, power_cycle, BMCreset"]

    parser = argparse.ArgumentParser(description='Power action on BMC and Host Server ')
    parser.add_argument("-H", "--host", action="store", type=str, required=True,
                        default=None, help="BMC IP address", metavar='')
    parser.add_argument("-u", "--username", action="store", type=str,
                        default="Administrator", help="Remote manager user name", metavar='')
    parser.add_argument("-p", "--password", action="store", type=str,
                        default="Administrator", help="Remote manager user password", metavar='')
    parser.add_argument("-M", "--module", action="store", type=int,
                        default=9999, help="Module number 0..17", metavar='', choices=range(0, 17))

    parser.add_argument("-a", "--action", action="store", type=str, default="status",
                        help="Power action. Poassible values are : {}".format(power_action_values),
                        metavar='', choices=power_action_values)

    # parser.add_argument("-v", "--verbose", action="store_false",  help="verbosity")

    args = parser.parse_args()

    obj_power.create(args.host, args.username, args.password)

    os.makedirs("/var/log/redfish/", exist_ok=True)
    log_file = "/var/log/redfish/" + __file__ + "_" + obj_power.bmc_ip + "_" + args.action + "_" \
               + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".log"
    obj_power.set_log(log_file)
    logging.info(__file__)

    if args.action == "BMCreset":
        if args.module == 9999:
            obj_power.reset_all()
        else:
            obj_power.reset_module(args.module)

        obj_power.wait_mc_available()

    elif args.action == "status":
        obj_power.status()
        print("Server {ip} : {st}".format(ip=obj_power.bmc_ip, st=obj_power.power_state))

    elif args.action == "off_force":
        obj_power.force_off()

    elif args.action == "on":
        obj_power.on()

    elif args.action == "off":
        obj_power.graceful_shutdown()

    elif args.action == "power_cycle":
        obj_power.force_cycle()

    else:
        parser.print_help()

except requests.exceptions.InvalidURL:
    print("Invalid URL")
    logging.exception(repr(traceback.extract_stack()))
except requests.exceptions.ConnectionError:
    print("Connection impossible unknown BMC IP address ....")
    logging.exception(repr(traceback.extract_stack()))
except KeyboardInterrupt:
    print("Program interrupt by user ")
except Exception:
    logging.exception(repr(traceback.extract_stack()))
finally:
    print("/!\\ Something bad happened. See log logfile {}".format(log_file))

sys.exit()
