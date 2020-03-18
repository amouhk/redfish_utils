import inspect
import logging
import traceback

import requests


class BMCInfo:
    def __init__(self):
        super().__init__()
        self.peb_type = ""
        self.server_info_tab = {}
        self.module_number = 0
        self.socket_number = 0
        self.memory_number = 0

    def get_peb_type(self):
        logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        data = {}
        resp = ""
        req_str = "http://" + self.bmc_ip + ":8080/redfish/v1/Systems/Server"
        try:
            resp = self.session.get(req_str, verify=False, auth=(self.username, self.password))
            data = resp.json()
            ret_data = data['BiosVersion']
            if ret_data[19] == 0:
                self.peb_type = "EPBS"
            else:
                self.peb_type = "PEB"
            logging.info("BiosVersion : " + ret_data + " - " + ret_data[19] + ": " + self.peb_type)
        except KeyError:
            logging.exception(repr(traceback.extract_stack()))
            logging.error("Key BiosVersion does not exists in " + req_str + " page")
            raise
        except IndexError:
            logging.exception(repr(traceback.extract_stack()))
            logging.error(ret_data + " indice 19 form BiosVersion impossible")
            raise

    def get_server_info(self):
        logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        data = {}
        resp = ""
        req_str = "http://" + self.bmc_ip + ":8080/redfish/v1/Systems/Server"
        try:
            resp = self.session.get(req_str, verify=False, auth=(self.username, self.password))
            data = resp.json()
            self.server_info_tab["ProductName"] = data['Model']
            self.server_info_tab["ManufacturerName"] = data['Manufacturer']
            self.server_info_tab["SerialNumber"] = data['SerialNumber']
            logging.info(" Server Model " + str(self.server_info_tab))
        except KeyError:
            logging.exception(repr(traceback.extract_stack()))
            logging.error("Key BiosVersion does not exists in " + req_str + " page")
            raise


