import datetime
import inspect
import os
import json
import logging
import pprint
import sys
import traceback
import time
import pycurl
import concurrent.futures

from tools.mesca3.redfish_utils.utils import find_between
from beautifultable import BeautifulTable
from tools.mesca3.redfish_utils.AccessBMC import AccessBMC


class Firmware(AccessBMC):
    def __init__(self):
        super().__init__()
        self.FW_LIST = ["BMC", "BIOS", "BIOS_BKUP", "Main_FPGA", "M3PCPLD", "M3IOCPLD", "WEO_FPGA", "WEO_BCM",
                        "PEB_FLASH", "PEBS_PHY_FLASH"]
        self.FW_UPG = ["BIOS", "BMC", "M3PCPLD", "M3IOCPLD", "MAIN_FPGA"]
        self.modules_firmwares = {}
        self.file_path = "file_path"
        self.fw_name = "fw_name"
        self.min_module_nb = 0
        self.max_module_nb = 0

    def set_firmware_file(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError("{} does not exists".format(file_path))
        self.file_path = file_path

    def append_firmwares(self, fw_name: str, pos: int, fw_ver: str):
        if fw_name not in self.modules_firmwares:
            mod_max = self.max_module_nb + 1
            self.modules_firmwares[fw_name] = ["" for i in range(self.min_module_nb, mod_max)]
            self.modules_firmwares[fw_name][0] = fw_name
        pos += 1
        self.modules_firmwares[fw_name][pos] = fw_ver

    def upload(self):
        logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        str_upd = "http://" + self.bmc_ip + ":8080/redfish/v1/UpdateService/Actions/Oem/Upload"

        # check fw file exist
        if not os.path.exists(self.file_path):
            raise Exception("Sorry, File \'{}\' doesn\'t exist ".format(self.file_path))

        # check fw name
        if self.fw_name not in self.FW_UPG:
            raise Exception(
                "Sorry, Cannot upload \'{}\' firmware tag.\nPossible value are {}".format(self.fw_name, self.FW_UPG))

        if self.fw_name == 'BIOS':
            print("Check PEB/PEBS")
            logging.info("str_upd")
            bios_ver_old = self.get_firmware_version(0, self.fw_name)
            bios_ver_new = os.path.basename(self.file_path)[9:21]
            logging.info("BIOS : {old}  vs {new}".format(old=bios_ver_old, new=bios_ver_new))
            if bios_ver_old[10] == '0':
                logging.info("Server is PEBS")
            else:
                logging.info("Server is PEB")
            if bios_ver_new[10] != bios_ver_old[10]:
                logging.info("Upload firmware is imcompatible with plateform")
                raise Exception("Upload firmware is imcompatible with plateform")

        logging.info("Copying on modules ....")
        logging.info("str_upd")
        print("Copying on modules ....")

        try:
            # create and execute curl commande
            curl_cmd = pycurl.Curl()
            curl_cmd.setopt(pycurl.URL, str_upd)
            curl_cmd.setopt(pycurl.PASSWORD, self.password)
            curl_cmd.setopt(pycurl.USERNAME, self.username)
            curl_cmd.setopt(pycurl.HTTPHEADER, ['Expect:'])
            send_data = [('name', self.fw_name), ('target', self.fw_name), ('file', (pycurl.FORM_FILE, self.file_path))]
            logging.info(send_data)
            curl_cmd.setopt(pycurl.HTTPPOST, send_data)
            curl_cmd.setopt(pycurl.VERBOSE, 0)
            curl_cmd.setopt(pycurl.WRITEFUNCTION, lambda bytes: len(bytes))
            curl_cmd.perform()
            curl_cmd.close()
        except Exception:
            raise

    def flash(self):
        logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        req_flash = "http://" + self.bmc_ip + ":8080/redfish/v1/UpdateService/Actions/SimpleUpdate"
        header = {'content-type': 'application/json'}
        payload = {'ImageURI': "http://" + self.bmc_ip + "/images/" + self.fw_name, 'TransferProtocol': 'HTTP'}
        self.session.post(req_flash, data=json.dumps(payload), headers=header, verify=True,
                          auth=(self.username, self.password))

    def cancel(self):
        logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        req_cancel = "http://" + self.bmc_ip + ":8080/redfish/v1/UpdateService/Actions/Oem/Discard"
        header = {'content-type': 'application/json'}
        payload = {'ImageURI': "http://" + self.bmc_ip + "/images/" + self.fw_name, 'TransferProtocol': 'HTTP'}

        self.session.post(req_cancel, data=json.dumps(payload), headers=header, verify=True,
                          auth=(self.username, self.password))

    def is_upload(self):
        logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        ret_code = False
        req_str = "http://" + self.bmc_ip + ":8080/redfish/v1/UpdateService"
        resp = ""
        try:
            resp = self.session.get(req_str, verify=False, auth=(self.username, self.password))
            data_json = resp.json()

            p_oem_start = "{\""
            p_oem_end = "\": {\""
            oem_str = find_between(json.dumps(data_json["Oem"]), p_oem_start, p_oem_end)

            upload_state = data_json["Oem"][oem_str]["update status"]  # update finished
            upload_fw_name = data_json["Oem"][oem_str]["last uploaded FW "]  # fw name : BIOS, BMC etc
            upload_fw_size = int(data_json["Oem"][oem_str]["last uploaded FW size "])  # fw name : BIOS, BMC etc

            expected_size = os.path.getsize(self.file_path)

            if (upload_fw_name == self.fw_name) or (upload_fw_size == expected_size):
                logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name +
                             ": Firmware upload status : OK")
                ret_code = True
            else:
                logging.error(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name +
                              ": Firmware upload status : NOK")
                ret_code = False

        except json.JSONDecodeError:
            logging.info(resp)
            logging.exception(repr(traceback.extract_stack()))
            ret_code = False
        except KeyError:
            logging.exception(repr(traceback.extract_stack()))
            ret_code = False
        except Exception:
            raise

        return ret_code

    def is_flashing(self):
        logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        req_str = "http://" + self.bmc_ip + ":8080/redfish/v1/UpdateService"
        ret_code = False
        resp = ""
        while True:
            try:
                resp = self.session.get(req_str, verify=False, auth=(self.username, self.password))
                data_json = resp.json()

                p_oem_start = "{\""
                p_oem_end = "\": {\""
                oem_str = find_between(json.dumps(data_json["Oem"]), p_oem_start, p_oem_end)

                flash_state = data_json["Oem"][oem_str]["update status"]

                if flash_state == "update finished":
                    print("[Success]", flash_state)
                    ret_code = True
                elif flash_state == "unknown or error":
                    print("[Failed]", flash_state)
                    ret_code = False
                else:
                    print(flash_state)
                    logging.info("state : " + flash_state)
                    ret_code = False
                    time.sleep(30)
                    continue
                logging.info("state : " + flash_state)
                break
            except KeyError:
                logging.exception(repr(traceback.extract_stack()))
            except json.JSONDecodeError:
                logging.info(resp)
                logging.exception(repr(traceback.extract_stack()))
            except Exception:
                raise
        return ret_code

    def get_firmware_version(self, module: int, name: str):
        logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        resp = ""
        ret_data = ""
        try:
            req_str = "http://" + self.bmc_ip + ":8080/redfish/v1/UpdateService/SoftwareInventory/Module" + str(
                module) + "_" + name
            resp = self.session.get(req_str, verify=False, auth=(self.username, self.password))
            data = resp.json()
            ret_data = data['Version']
        except KeyError as key_error:
            ret_data = "Not Supported"
        except json.JSONDecodeError:
            logging.info(resp)
            logging.exception(repr(traceback.extract_stack()))

        if name == "BIOS" or name == 'BIOS_BKUP':
            ret_data = ret_data[9:]

        if name == "BMC":
            ret_data = ret_data[:7]

        if name == 'Main_FPGA':
            ret_data = ret_data.replace('DBG', '')

        # logging.info("{:25} : {}".format(data["Id"], ret_data))
        logging.info(str(resp))
        return ret_data

    def get_modules_number(self):
        logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        mod_nb = 0
        req_str = ""
        resp = ""
        try:
            req_str = "http://" + self.bmc_ip + ":8080/redfish/v1/Chassis"
            resp = self.session.get(req_str, auth=(self.username, self.password))
            data = resp.json()
            mod_nb = int(data['Members@odata.count'])
        except Exception:
            logging.info(resp)
            raise

        logging.info("Module Number : " + str(mod_nb))
        return mod_nb

    def get_firmware_from_name(self, module_id: int):
        logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)

        self.min_module_nb = 0
        self.max_module_nb = self.get_modules_number()

        if module_id != 9999:
            self.min_module_nb = module_id
            self.max_module_nb = module_id + 1

        if self.fw_name not in self.FW_LIST:
            raise Exception(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name +
                            " " + self.fw_name + "does not exist")
        print("Getting info ... ")
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_module_nb) as mod_executor:
            future_mods = {mod_executor.submit(self.get_firmware_version, id, self.fw_name): id for id in
                           range(self.min_module_nb, self.max_module_nb)}
            for future in concurrent.futures.as_completed(future_mods):
                print("Module {}".format(future_mods[future]))
                print("\t{name} : {ver}".format(name=self.fw_name, ver=future.result()))
        print("")

    # Get on module firmware
    def thread_get_module_firmwares(self, module):
        logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name + ": " + str(module))
        # sys.stdout.write("Getting firmwares info ")
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.FW_LIST)) as fw_executor:
            future_to_fw = {fw_executor.submit(self.get_firmware_version, module, fw): fw for fw in self.FW_LIST}
            for future in concurrent.futures.as_completed(future_to_fw):
                fw_name = future_to_fw[future]
                try:
                    data = future.result()
                except Exception:
                    logging.exception(repr(traceback.extract_stack()))
                    logging.exception("{f_name:18}: {f_ver}".format(f_name=fw_name, f_ver=data))
                else:
                    logging.info("{f_name:18}: {f_ver}".format(f_name=fw_name, f_ver=data))
                    sys.stdout.write('.')
                    sys.stdout.flush()
                    self.append_firmwares(fw_name, module, data)

    def get_all_firmware(self, module_id: int):
        logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        # Get number of module in the partition
        req_str_chassis = "http://" + self.bmc_ip + ":8080/redfish/v1/Chassis"
        self.min_module_nb = 0
        self.max_module_nb = self.get_modules_number()

        if module_id != 9999:
            self.min_module_nb = module_id
            self.max_module_nb = module_id + 1

        print(" end thr2 " + datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        sys.stdout.write("Getting firmwares info ")
        sys.stdout.flush()
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_module_nb) as mod_executor:
            future_mods = {mod_executor.submit(self.thread_get_module_firmwares, id): id for id in
                           range(self.min_module_nb, self.max_module_nb)}

        table = BeautifulTable()
        table.set_style(BeautifulTable.STYLE_GRID)
        fw_column_header = ["Component"]
        for module in range(self.min_module_nb, self.max_module_nb):
            fw_column_header.append("Module " + str(module))
        table.append_row(fw_column_header)
        for key_name in sorted(self.modules_firmwares.keys()):
            table.append_row(self.modules_firmwares[key_name])
        print("")
        print(table)
        print(" end thr2 " + datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))

    def get_firmware_inventory(self):
        logging.info(self.__class__.__name__ + ":" + inspect.currentframe().f_code.co_name)
        ret_code = False
        firm_mod_dict = {}
        req_str = "http://" + self.bmc_ip + ":8080/redfish/v1/UpdateService/SoftwareInventory"
        resp = ""
        try:
            resp = self.session.get(req_str, verify=False, auth=(self.username, self.password))
            data_json = resp.json()
            str_pre = "/redfish/v1/UpdateService/SoftwareInventory/Module"
            fw_number = int(data_json['Members@odata.count'])
            mod_id_list = []
            for fw_id in range(fw_number):
                o_data_id = data_json['Members'][fw_id]['@odata.id']
                module_id = int(o_data_id[len(str_pre):o_data_id.find('_')])
                if module_id not in mod_id_list:
                    firm_mod_dict[module_id] = []
                    mod_id_list.append(module_id)
                fw_name = o_data_id.replace(str_pre + str(module_id) + '_', '')
                # print("Firmware Num {} : {}".format(module_id, fw_name))
                firm_mod_dict[module_id].append(fw_name)

            # pprint.pprint(firm_mod_dict)
            return firm_mod_dict

        except json.JSONDecodeError:
            logging.info(resp)
            logging.exception(repr(traceback.extract_stack()))
            ret_code = False
        except KeyError:
            logging.exception(repr(traceback.extract_stack()))
            ret_code = False
        except Exception:
            raise

