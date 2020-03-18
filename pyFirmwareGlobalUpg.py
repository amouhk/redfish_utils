import getopt
import os
import pprint
import sys
import traceback
import xml.etree.ElementTree as xml

from Firmware import Firmware

from BMCInfo import BMCInfo


def usage():
    print('\n' + __file__ + ' usage:')
    print('  -h   display usage and exit')
    print('  -u   user name,                                              default Administrator')
    print('  -p   password,                                               default Administrator ')
    print('  -H   IP address,                                             default 172.31.100.156')
    print('  -M   Module Id,                                              default x')
    print('  -a   Action (list|),                                         default: list')
    print('  -D   Technical state dir,                                    default: ')
    print('  -v   Verbose (N|Y),                                          Versbose')
    print('\n')
    sys.exit()


def list_technical_state_info(xml_root: xml.Element, product_name: str):
    print("")
    print("TECHNICAL STATE FIRMWARE INFORMATION")

    ts_info = xml_root.find("TS_INFO")

    print("")
    print("  {title:10} : {srv} {ts}".format(title="INPUT TS", srv=ts_info.find("NAME").text,
                                             ts=ts_info.find("VERSION").text))
    print("  {title:10} : {date}".format(title="DATE", date=ts_info.find("DATE").text))

    print("")
    first = True
    for fw in xml_root.iter('FW'):
        for prod_id in fw.findall("PRODUCT_ID_LIST/PRODUCT_ID"):
            if product_name.lower() in prod_id.text.lower():
                if first:
                    print("  {title} : {val}".format(title="FIRMWARE LIST FOR PRODUCT_ID", val=prod_id.text))
                    print("")
                    first = False
                print("\t{title:25} : {val}".format(title="FW NAME", val=fw.find("NAME").text))
                print("\t{title:25} : {val}".format(title="FW VERSION", val=fw.find("VERSION").text))
                print("\t{title:25} : {val}".format(title="FW DIFF", val=fw.find("MANAGEABILITY/DIFF_VERSION").text))
                print("\t{title:25} : {val}".format(title="FW UPGRADE", val=fw.find("MANAGEABILITY/UPDATE_FW").text))
                print("\t{title:25} : {val}".format(title="COMPONENT_ID LIST", val=fw.find("COMPONENT_ID_LIST"
                                                                                           "/COMPONENT_ID").text))
        print("")


def diff_info(xml_root: xml.Element, o_firmware: Firmware, o_bmc: BMCInfo):
    print("FIRMWARE DIFF FOR")
    print(
        "\t{:16} : {} {}".format("INPUT TS", xml_root.find("TS_INFO/NAME").text, xml_root.find("TS_INFO/VERSION").text))
    print("\t{:16} : {}".format("HOST ADDRESS", o_bmc.bmc_ip))
    print("\t{:16} : {}".format("HOST PRODUCT ID", obj_bmc.server_info_tab["ProductName"]))
    print("\t{:16} : {}".format("CURRENT HOST TS", ""))

    print("")
    mods_fw_tab = o_firmware.get_firmware_inventory()
    for m_id in sorted(mods_fw_tab.keys()):
        for fw_node in xml_root.iter('FW'):
            fw_ts_name = fw_node.find('NAME').text
            print(" fw_ts_name : " + fw_ts_name)
            fw_srv_name = MAP_FW_TS_SERVER[fw_ts_name]
            print(" fw_srv_name : " + fw_srv_name)
            if fw_srv_name in mods_fw_tab[m_id]:
                print("{fw_ts_name} {fw_srv_name}".format(fw_ts_name=fw_ts_name, fw_srv_name=fw_srv_name))

    # for m_id in sorted(mods_fw_tab.keys()):
    #     print("\t{:16} : {}".format("MODULE ID", str(m_id)))
    #     for fw_name in sorted(mods_fw_tab[m_id]):
    #         print(" FW NAME : " + fw_name)
    #         ts_fw = MAP_FW_SERVER_TS[fw_name]
    #         print(xml_root.findall("FW_LIST/FW/NAME"))
    #     print("")


MAP_FW_TS_SERVER = {"EMM33_BMC": "BMC",
                    "EMM34_LMC": "LMC",
                    "FPGA_CPB": "MAIN_FPGA",
                    "FPGA_LMB_Multi": "Main_Multi",
                    "FPGA_LMB_Mng": "Main_Mngt",
                    "CPLD_P_CPB": "M3PCPLD",
                    "CPLD_IO_CPB": "M3IOCPLD",
                    "CPLD_LMB": "CPLD",
                    "FPGA_UNB0": "UNB0_FPGA",
                    "FPGA_UNB1": "UNB1_FPGA",
                    "FPGA_UNB2": "UNB2_FPGA",
                    "FPGA_UNB3": "UNB3_FPGA",
                    "ETH_SWITCH_LMB1": "",
                    "ETH_SWITCH_LMB2": "",
                    "CLK_UNB0": "UNB0_CLK",
                    "CLK_UNB1": "UNB1_CLK",
                    "CLK_UNB2": "UNB2_CLK",
                    "CLK_UNB3": "UNB3_CLK",
                    "BIOS_PUR043_PEB": "",
                    "BIOS_PUR043_PEBS": ""}

MAP_FW_SERVER_TS = {"BMC": "EMM33_BMC",
                    "LMC": "EMM34_LMC",
                    "MAIN_FPGA": "FPGA_CPB",
                    "Main_Multi": "FPGA_LMB_Mult",
                    "Main_Mngt": "FPGA_LMB_Mng",
                    "M3PCPLD": "CPLD_P_CPB",
                    "M3IOCPLD": "CPLD_IO_CPB",
                    "CPLD": "CPLD_LMB",
                    "UNB0_FPGA": "FPGA_UNB0",
                    "UNB1_FPGA": "FPGA_UNB1",
                    "UNB2_FPGA": "FPGA_UNB2",
                    "UNB3_FPGA": "FPGA_UNB3",
                    "sw_lmb1": "ETH_SWITCH_LMB1",
                    "sw_lmb2": "ETH_SWITCH_LMB2",
                    "UNB0_CLK": "CLK_UNB0",
                    "UNB1_CLK": "CLK_UNB1",
                    "UNB2_CLK": "CLK_UNB2",
                    "UNB3_CLK": "CLK_UNB3",
                    "BIOS1": "BIOS_PUR043_PEB",
                    "BIOS2": "BIOS_PUR043_PEBS"}

obj_firm = Firmware()
obj_bmc = BMCInfo()

module_id = 9999
action = "list"
action_step = "all"
verbose = ""
root_directory = ""
# parse args
try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "h:u:p:H:M:a:D:v:")
    for opt, arg in opts:
        if opt in '-h':
            usage()
        elif opt in '-u':
            obj_firm.username = arg
        elif opt in '-p':
            obj_firm.password = arg
        elif opt in '-H':
            obj_firm.bmc_ip = arg
        elif opt in '-M':
            module_id = int(arg)
        elif opt in '-a':
            action = arg
        elif opt in '-D':
            root_directory = arg
            if not os.path.isdir(root_directory):
                print("Directory " + root_directory + " does not exist")
                usage()
            root_directory = arg
        elif opt in '-v':
            verbose = arg

    if root_directory == "":
        print("Argument -D is mandatory")
        usage()

except getopt.GetoptError:
    print("Error parsing options")
    usage()
except Exception:
    traceback.print_exc()
    usage()

obj_bmc.create(obj_firm.bmc_ip, obj_firm.username, obj_firm.password)

technical_state_file = root_directory + "/Resources/TechnicalState.xml"
if not os.path.exists(technical_state_file) or not os.path.isfile(technical_state_file):
    print("Given directory \"" + root_directory + "\" is not a Technical State directory")
    usage()

tree = xml.parse(technical_state_file)
ts_xml_root = tree.getroot()

obj_bmc.get_server_info()

if action == "list":
    list_technical_state_info(ts_xml_root, obj_bmc.server_info_tab["ManufacturerName"])

if action == "diff":
    diff_info(ts_xml_root, obj_firm, obj_bmc)

if action == "check":
    print("action check")

if action == "upg":
    print("upgrading ")

if action == "test":
    print("test")
