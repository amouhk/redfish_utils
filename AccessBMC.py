import inspect
import json
import logging
import sys
import time
import traceback

import requests
import ipaddress

class AccessBMC:
    def __init__(self):
        self.password = "Administrator"
        self.username = "Administrator"
        self.bmc_ip = "bmc_ip"

        self.session = requests.Session()
        self.session.trust_env = False
        self.logging_file = ""

    def set_bmc_ip_address(self, a_bmc_ip):
        logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        try:
            ipaddress.ip_address(a_bmc_ip)
        except ValueError:
            print("Error : {} is not an ip address".format(a_bmc_ip))
            raise
        else:
            self.bmc_ip = a_bmc_ip

    def create(self, bmc_ip, usr, pwd):
        self.password = pwd
        self.username = usr
        self.set_bmc_ip_address(bmc_ip)

    def set_log(self, file):
        self.logging_file = file
        logging.basicConfig(filename=file, level=logging.DEBUG)

    def post_request(self, req, payload, header):
        resp = ""
        try:
            resp = self.session.post(req, data=json.dumps(payload), headers=header, verify=True, auth=(self.username, self.password))
            data = resp.json()
            logging.info(data)
            print(data["@Message.ExtendedInfo"][0]["Message"])
        except KeyError:
            logging.info(resp)
            logging.exception(repr(traceback.extract_stack()))
            print("Failed to completed request")
            raise
        except json.JSONDecodeError:
            logging.info(resp)
            logging.exception(repr(traceback.extract_stack()))
            print("Failed to completed request")
            raise

    def wait_mc_available(self):
        logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        print(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        data = {}
        resp = ""
        req_str = "http://" + self.bmc_ip + ":8080/redfish/v1/AccountService"
        sys.stdout.write('BMC is restarting ....')
        time.sleep(5)
        while True:
            try:
                resp = self.session.get(req_str, verify=False, auth=(self.username, self.password))
                data = resp.json()
                ret_data = data['Status']['Health']
                if ret_data == "OK":
                    print("\nBMC started OK")
                    break
            except Exception:
                # logging.exception(repr(traceback.extract_stack()))
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(15)
