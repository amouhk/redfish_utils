import inspect
import json
import logging
import pprint
import sys
import time
import traceback
import requests

from tools.mesca3.redfish_utils.AccessBMC import AccessBMC


class PowerAction(AccessBMC):
    def __init__(self):
        super().__init__()
        self.power_state = ""

    def wait_server_up(self):
        print("TODO")

    def reset_all(self):
        logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        print(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        req_rst = "http://" + self.bmc_ip + ":8080/redfish/v1/Managers/BMC_0/Actions/Manager.Reset"
        header = {'content-type': 'application/json'}
        payload = {'ResetType': 'IPMIColdReset'}
        resp = self.post_request(req_rst, payload, header)

    def reset_module(self, module: int):
        logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        print(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        req_rst = "http://" + self.bmc_ip + ":8080/redfish/v1/Managers/BMC_" + str(module) + "/Actions/Manager.Reset"
        logging.info(req_rst)
        header = {'content-type': 'application/json'}
        payload = {'ResetType': 'IPMIColdReset'}
        resp = self.post_request(req_rst, payload, header)

    def force_off(self):
        req_pwr = "http://" + self.bmc_ip + ":8080/redfish/v1/Systems/Server/Actions/ComputerSystem.Reset"
        header = {'content-type': 'application/json'}
        payload = {'ResetType': 'ForceOff'}
        resp = self.post_request(req_pwr, payload, header)

    def force_cycle(self):
        req_pwr = "http://" + self.bmc_ip + ":8080/redfish/v1/Systems/Server/Actions/ComputerSystem.Reset"
        header = {'content-type': 'application/json'}
        payload = {'ResetType': 'ForceRestart'}
        resp = self.post_request(req_pwr, payload, header)

    def on(self):
        req_pwr = "http://" + self.bmc_ip + ":8080/redfish/v1/Systems/Server/Actions/ComputerSystem.Reset"
        header = {'content-type': 'application/json'}
        payload = {'ResetType': 'On'}
        resp = self.post_request(req_pwr, payload, header)

    def graceful_shutdown(self):
        req_pwr = "http://" + self.bmc_ip + ":8080/redfish/v1/Systems/Server/Actions/ComputerSystem.Reset"
        header = {'content-type': 'application/json'}
        payload = {'ResetType': 'GracefulShutdown'}
        resp = self.post_request(req_pwr, payload, header)

    def status(self):
        logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        data = {}
        resp = ""
        req_str = "http://" + self.bmc_ip + ":8080/redfish/v1/Systems/Server"
        try:
            resp = self.session.get(req_str, verify=False, auth=(self.username, self.password))
            data = resp.json()
            # pprint.pprint(data)
            self.power_state = data['PowerState']
            logging.info(" PowerSate : " + self.power_state)
        except KeyError:
            logging.exception(repr(traceback.extract_stack()))
            logging.error("Key PowerState does not exists in " + req_str + " page")
            raise

    def clear_log(self, module_id):
        logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        req_clr = "http://" + self.bmc_ip + ":8080/redfish/v1/Managers/BMC_" \
                  + str(module_id) + "/LogServices/SEL/Actions/LogService.ClearLog"
        header = {'content-type': 'application/json'}
        payload = {'ClearType': 'ClearAll'}
        print("clear_log")
        self.session.post(req_clr, data=json.dumps(payload), headers=header, verify=True,
                          auth=(self.username, self.password))
