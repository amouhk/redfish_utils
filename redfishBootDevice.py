import argparse
import datetime
import json
import logging
import os
import sys
import traceback

from BootOption import BootOption

obj_boot_option = BootOption()
log_file = ""

try:

    parser = argparse.ArgumentParser(description='Boot Device Options ')
    parser.add_argument("-H", "--host", action="store", type=str, required=True,
                        default=None, help="BMC IP address", metavar='')
    parser.add_argument("-u", "--username", action="store", type=str,
                        default="Administrator", help="Remote manager user name", metavar='')
    parser.add_argument("-p", "--password", action="store", type=str,
                        default="Administrator", help="Remote manager user password", metavar='')
    parser.add_argument("-M", "--module", action="store", type=int,
                        default=9999, help="Module number 0..17", metavar='', choices=range(0, 17))

    parser.add_argument("-a", "--action", action="store", type=str,
                        default="get", help=" action [ get | set ]", metavar='', choices=['get', 'set'])
    parser.add_argument("-d", "--device", action="store", type=str, default="None",
                        help="Boot device. Poassible values are : {}".format(obj_boot_option.device_values),
                        metavar='', choices=obj_boot_option.device_values)
    parser.add_argument("-i", "--instance", action="store", type=str, default="0",
                        help="instance number of boot devices disk and pxe (possible values: from 0 to 15)",
                        metavar='', choices=obj_boot_option.inst_values)
    parser.add_argument("-P", "--persistant", action="store", type=str, default="no",
                        help="Make this choice persistant. Possible values are [ no | yes ]",
                        metavar='', choices=obj_boot_option.boolean_values)
    parser.add_argument("-c", "--clear_cmos", action="store", type=str, default="no",
                        help="Clear CMOS at next boot. Possible values are [ no | yes ]",
                        metavar='', choices=obj_boot_option.boolean_values)
    # parser.add_argument("-v", "--verbose", action="store_false",  help="verbosity")

    args = parser.parse_args()

    obj_boot_option.create(args.host, args.username, args.password)

    os.makedirs("/var/log/redfish/", exist_ok=True)
    log_file = "/var/log/redfish/" + __file__ + "_" + obj_boot_option.bmc_ip + "_" + args.action + "_" \
               + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".log"
    obj_boot_option.set_log(log_file)
    logging.info(__file__)

    obj_boot_option.set_device(args.device)
    obj_boot_option.set_instance(args.instance)
    obj_boot_option.set_clr_cmos(args.clear_cmos)
    obj_boot_option.set_persistant(args.persistant)

    if args.action == "set":
        obj_boot_option.apply_option()

    obj_boot_option.get_options()
    obj_boot_option.print_option()

except KeyError:
    logging.exception(repr(traceback.extract_stack()))
except json.JSONDecodeError:
    logging.exception(repr(traceback.extract_stack()))
except ValueError:
    logging.exception(repr(traceback.extract_stack()))
except KeyboardInterrupt:
    print("Program interrupt by user ")
except Exception:
    logging.exception(repr(traceback.extract_stack()))
finally:
    print("/!\\ Something bad happened. See log logfile {}".format(log_file))

sys.exit()
