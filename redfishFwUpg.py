import argparse
import datetime
import logging
import os
import sys
import time
import traceback

import requests
from Firmware import Firmware
from PowerAction import PowerAction

obj_firmware = Firmware()
obj_power = PowerAction()
log_file = ""

action_values = ["ver", "list", "upg", "step", "inventory"]
step_action_values = ["all", "upload", "check", "flash", "status", "cancel"]

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

    parser.add_argument("-a", "--action", action="store", type=str, default="list",
                        help="Possible values : {}".format(action_values), metavar='', choices=action_values)
    parser.add_argument("-s", "--step", action="store", type=str, default="all",
                        help="Upg action step. Possible values : {}".format(step_action_values),
                        metavar='', choices=step_action_values)
    parser.add_argument("-F", "--File", action="store", type=str, default=None, help="Firmware file path", metavar='')
    parser.add_argument("-E", "--FwName", action="store", type=str, default=None,
                        help="Name of the firmware to be upload. Possible values : {}".format(obj_firmware.FW_UPG),
                        metavar='', choices=obj_firmware.FW_UPG)
    # parser.add_argument("-v", "--verbose", action="store_false",  help="verbosity")

    args = parser.parse_args()

    obj_firmware.create(args.host, args.username, args.password)
    obj_power.create(args.host, args.username, args.password)

    os.makedirs("/var/log/redfish/", exist_ok=True)
    log_file = "/var/log/redfish/" + __file__ + "_" + obj_firmware.bmc_ip + \
               "_" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".log"
    obj_firmware.set_log(log_file)
    obj_power.set_log(log_file)
    logging.info(__file__)

    obj_firmware.set_firmware_file(args.File)
    obj_firmware.fw_name = args.FwName

    if args.action == "ver":
        if args.module == 9999:
            print(" Missing argument -M <module_id>")
            parser.print_help()

        if obj_firmware.fw_name == "":
            print(" Missing argument -E <firmware name>")
            parser.print_help()

        obj_firmware.get_firmware_version(args.module, obj_firmware.fw_name)

    if args.action == "list":
        obj_firmware.get_all_firmware(args.module)

    if args.action == "upg":
        if args.step == "upload":
            obj_firmware.upload()

        elif args.step == "check":
            if obj_firmware.is_upload():
                print("Firmware file is present OK")
                logging.info("Firmware file is present OK")
            else:
                print("Firmware file not present NOK")
                logging.info("Firmware file not present NOK")

        elif args.step == "flash":
            obj_firmware.flash()

        elif args.step == "status":
            obj_firmware.is_flashing()

        elif args.step == "cancel":
            obj_firmware.cancel()

        else:
            logging.info("update all step")

            obj_firmware.cancel()
            time.sleep(5)

            obj_firmware.upload()
            time.sleep(5)

            if not obj_firmware.is_upload():
                logging.error("Firmware " + obj_firmware.fw_name + "is not correctly upload")
                logging.error(obj_firmware.fw_name + " : " + obj_firmware.file_path)
                sys.exit(1)

            obj_firmware.flash()
            obj_firmware.is_flashing()

            if obj_firmware.fw_name == "BMC":
                obj_power.reset()
                obj_power.wait_mc_available()

    if args.action == "inventory":
        obj_firmware.get_firmware_inventory()


except requests.exceptions.InvalidURL as ex_url:
    print("Invalid URL")
    logging.exception(repr(traceback.extract_stack()))
except requests.exceptions.ConnectionError as ex_cnt:
    print("Connection impossible unknown BMC IP address ....")
    logging.exception(repr(traceback.extract_stack()))
except KeyboardInterrupt:
    print("Program interrupt by user ")
except Exception:
    logging.exception(repr(traceback.extract_stack()))
finally:
    print("/!\\ Something bad happened. See log logfile {}".format(log_file))

sys.exit()

