import datetime
import getopt
import logging
import os
import sys
import time
import traceback

import requests
from tools.mesca3.redfish_utils.Firmware import Firmware
from tools.mesca3.redfish_utils.PowerAction import PowerAction


def usage():
    print('\n' + __file__ + 'usage:')
    print('  -h   display usage and exit')
    print('  -u   user name,                                              default Administrator')
    print('  -p   password,                                               default Administrator ')
    print('  -H   IP address,                                             default 172.31.100.156')
    print('  -M   Module Id,                                              default x')
    print('  -a   Action (ver|list|upg|step),                                 default: list')
    print('  -s   Action step(all|upload|check|flash|status|cancel)       default all')
    print('  -F   Firmware filepath                                       *')
    print('  -E   Firmware type,                                          BMC | BIOS | M3IOCPLD | M3PCPLD | MAIN_FPGA')
    print('  -v   Verbose (N|Y),                                          Versbose')
    print('\n')
    sys.exit()


obj_firmware = Firmware()
obj_power = PowerAction()

module_id = 9999
action = "list"
action_step = "all"
verbose = ""
# parse args
try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "h:u:p:H:M:a:s:F:E:v:")
    for opt, arg in opts:
        if opt in '-h':
            usage()
        elif opt in '-u':
            obj_firmware.username = arg
        elif opt in '-p':
            obj_firmware.password = arg
        elif opt in '-H':
            obj_firmware.bmc_ip = arg
        elif opt in '-F':
            obj_firmware.file_path = arg
        elif opt in '-E':
            obj_firmware.fw_name = arg
        elif opt in '-M':
            module_id = int(arg)
        elif opt in '-a':
            action = arg
        elif opt in '-s':
            action_step = arg

        elif opt in '-v':
            verbose = arg

except getopt.GetoptError:
    print("Error parsing options")
    usage()
except Exception:
    traceback.print_exc()
    usage()

obj_power.create(bmc_ip=obj_firmware.bmc_ip, usr=obj_firmware.username, pwd=obj_firmware.password)

try:
    os.makedirs("/var/log/redfish/", exist_ok=True)
    log_file = "/var/log/redfish/" + __file__ + "_" + obj_firmware.bmc_ip + \
               "_" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".log"
    obj_firmware.set_log(log_file)

    logging.info(__file__)

    if action == "ver":
        if module_id == 9999:
            print(" Missing argument -M <module_id>")
            usage()
        if obj_firmware.fw_name == "":
            print(" Missing argument -E <firmware name>")
            usage()

        obj_firmware.get_firmware_version(int(module_id), obj_firmware.fw_name)

    if action == "list":
        obj_firmware.get_all_firmware(module_id)

    if action == "upg":
        if action_step == "all":
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

        elif action_step == "upload":
            obj_firmware.upload()

        elif action_step == "check":
            if obj_firmware.is_upload():
                print("Firmware file is present OK")
                logging.info("Firmware file is present OK")
            else:
                print("Firmware file not present NOK")
                logging.info("Firmware file not present NOK")

        elif action_step == "flash":
            obj_firmware.flash()

        elif action_step == "status":
            obj_firmware.is_flashing()

        elif action_step == "cancel":
            obj_firmware.cancel()

    if action == "inventory":
        obj_firmware.get_firmware_inventory()


except requests.exceptions.InvalidURL as ex_url:
    traceback.print_exc()
    logging.exception(repr(traceback.extract_stack()))
    usage()
except requests.exceptions.ConnectionError as ex_cnt:
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
