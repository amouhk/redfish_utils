import inspect
import json
import logging
import requests

from AccessBMC import AccessBMC


class BootOption(AccessBMC):
    def __init__(self):
        super().__init__()
        self.device_values = ["None", "Pxe", "Disk", "Diag", "Bios"]
        self.inst_values = range(0, 15, 1)
        self.boolean_values = ["no", "yes"]

        self.device = "None"
        self.instance = "0"
        self.clr_cmos = "no"
        self.persistant = "no"

        self.session = requests.Session()
        self.session.trust_env = False
        self.logging_file = ""

    def set_device(self, a_device):
        if a_device not in self.device_values:
            print("Error : Incorrect device name \"" + a_device + "\"")
            raise Exception("Device name must be in {} ".format(self.device_values))
        self.device = a_device

    def set_instance(self, a_inst: str):
        try:
            l_inst = int(a_inst)
            if l_inst not in self.inst_values:
                print("Error : Incorrect instance number \"" + a_inst + "\"")
                raise Exception("Device name must be in {} ".format(self.device_values))
            self.instance = l_inst
        except ValueError:
            raise Exception("Error : \"{}\" is not an interger.".format(a_inst))

    def set_clr_cmos(self, a_bool: str):
        if a_bool not in self.boolean_values:
            print("Error : Incorrect value \"" + a_bool + "\"")
            raise Exception("Value must be in {}".format(self.boolean_values))
        self.clr_cmos = a_bool

    def set_persistant(self, a_bool: str):
        if a_bool not in self.boolean_values:
            print("Error : Incorrect value \"" + a_bool + "\"")
            raise Exception("Value must be in {}".format(self.boolean_values))
        self.persistant = a_bool

    def print_option(self):
        print("BOOT OPTION :")
        print("\t{:12}: {}".format("Device", self.device))
        print("\t{:12}: {}".format("Instance", self.instance))
        print("\t{:12}: {}".format("ClearCMOS", self.clr_cmos))
        print("\t{:12}: {}".format("Persistant", self.persistant))

    def apply_option(self):
        logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        # print(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        req_rst = "http://" + self.bmc_ip + ":8080/redfish/v1/Systems/Server/Actions/Oem/ComputerSystem.SetBootOption"
        header = {'content-type': 'application/json'}
        payload = {"Boot": {"BootSourceOverrideTarget": self.device, "instance": str(self.instance),
                            "clearcmos": self.clr_cmos, "persistent": self.persistant}}
        self.post_request(req_rst, payload, header)

    def get_options(self):
        logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        print("TODO: Not yet implemented")
        # resp = ""
        # try:
        #     req_rst = "http://" + self.bmc_ip + ":8080/redfish/v1/Systems/Server"
        #     resp = self.session.get(req_rst, verify=False, auth=(self.username, self.password))
        #     data = resp.json()
        #     self.device = data["Boot"]["BootSourceOverrideTarget"]
        #     self.instance = data["Boot"]["BootSourceOverrideTarget@Redfish.AllowableValues"]
        #     self.clr_cmos = ""
        #     self.persistant = ""
        # except KeyError:
        #     logging.info(resp)
        #     print("Failed to completed request")
        #     raise
        # except json.JSONDecodeError:
        #     logging.info(resp)
        #     print("Failed to completed request")
        #     raise
