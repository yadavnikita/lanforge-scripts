# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Define useful common methods                                  -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()
import os
import pprint
import time
from time import sleep
from random import seed

seed(int(round(time.time() * 1000)))
from random import randint
from LANforge import LFRequest

debug_printer = pprint.PrettyPrinter(indent=2)

NA = "NA"  # used to indicate parameter to skip
ADD_STA_FLAGS_DOWN_WPA2 = 68719477760
REPORT_TIMER_MS_FAST = 1500
REPORT_TIMER_MS_SLOW = 3000


class PortEID:
    shelf = 1
    resource = 1
    port_id = 0
    port_name = ""

    def __init__(self, p_resource=1, p_port_id=0, p_port_name=""):
        resource = p_resource
        port_id = p_port_id
        port_name = p_port_name

    def __init__(self, json_response):
        if json_response == None:
            raise Exception("No json input")
        json_s = json_response
        if json_response['interface'] != None:
            json_s = json_response['interface']

        debug_printer(json_s)
        resource = json_s['resource']
        port_id = json_s['id']
        port_name = json_s['name']


# end class PortEID

def staNewDownStaRequest(sta_name, resource_id=1, radio="wiphy0", ssid="", passphrase="", debug_on=False):
    return sta_new_down_sta_request(sta_name, resource_id, radio, ssid, passphrase, debug_on)

def sta_new_down_sta_request(sta_name, resource_id=1, radio="wiphy0", ssid="", passphrase="", debug_on=False):
    """
    For use with add_sta. If you don't want to generate mac addresses via patterns (xx:xx:xx:xx:81:*)
    you can generate octets using random_hex.pop(0)[2:] and gen_mac(parent_radio_mac, octet)
    See http://localhost:8080/help/add_sta
    :param passphrase:
    :param ssid:
    :type sta_name: str
    """
    data = {
        "shelf": 1,
        "resource": resource_id,
        "radio": radio,
        "sta_name": sta_name,
        "flags": ADD_STA_FLAGS_DOWN_WPA2,  # note flags for add_sta do not match set_port
        "ssid": ssid,
        "key": passphrase,
        "mac": "xx:xx:xx:xx:*:xx",  # "NA", #gen_mac(parent_radio_mac, random_hex.pop(0))
        "mode": 0,
        "rate": "DEFAULT"
    }
    if (debug_on):
        debug_printer.pprint(data)
    return data


def portSetDhcpDownRequest(resource_id, port_name, debug_on=False):
    return port_set_dhcp_down_request(resource_id, port_name, debug_on)

def port_set_dhcp_down_request(resource_id, port_name, debug_on=False):
    """
    See http://localhost:8080/help/set_port
    :param resource_id:
    :param port_name:
    :return:
    """
    print("portSetDhcpDownRequest")
    data = {
        "shelf": 1,
        "resource": resource_id,
        "port": port_name,
        "current_flags": 2147483649,  # 0x1 = interface down + 2147483648 use DHCP values
        "interest": 75513858,  # includes use_current_flags + dhcp + dhcp_rls + ifdown
        "report_timer": REPORT_TIMER_MS_FAST
    }
    if (debug_on):
        debug_printer.pprint(data)
    return data


def portDhcpUpRequest(resource_id, port_name, debug_on=False):
    return port_dhcp_up_request(resource_id, port_name, debug_on)

def port_dhcp_up_request(resource_id, port_name, debug_on=False):
    """
    See http://localhost:8080/help/set_port
    :param resource_id:
    :param port_name:
    :return:
    """
    print("portDhcpUpRequest")
    data = {
        "shelf": 1,
        "resource": resource_id,
        "port": port_name,
        "current_flags": 2147483648,  # vs 0x1 = interface down + use_dhcp
        "interest": 75513858,  # includes use_current_flags + dhcp + dhcp_rls + ifdown
        "report_timer": REPORT_TIMER_MS_FAST,
    }
    if (debug_on):
        debug_printer.pprint(data)
    return data


def portUpRequest(resource_id, port_name, debug_on=False):
    return port_up_request(resource_id, port_name, debug_on)

def port_up_request(resource_id, port_name, debug_on=False):
    """
    See http://localhost:8080/help/set_port
    :param resource_id:
    :param port_name:
    :return:
    """
    data = {
        "shelf": 1,
        "resource": resource_id,
        "port": port_name,
        "current_flags": 0,  # vs 0x1 = interface down
        "interest": 8388610,  # includes use_current_flags + dhcp + dhcp_rls + ifdown
        "report_timer": REPORT_TIMER_MS_FAST,
    }
    if (debug_on):
        print("Port up request")
        debug_printer.pprint(data)
    return data

def portDownRequest(resource_id, port_name, debug_on=False):
    return port_down_request(resource_id, port_name, debug_on)

def port_down_request(resource_id, port_name, debug_on=False):
    """
    Does not change the use_dhcp flag
    See http://localhost:8080/help/set_port
    :param resource_id:
    :param port_name:
    :return:
    """
    
    data = {
        "shelf": 1,
        "resource": resource_id,
        "port": port_name,
        "current_flags": 1,  # vs 0x0 = interface up
        "interest": 8388610,  # = current_flags + ifdown
        "report_timer": REPORT_TIMER_MS_FAST,
    }
    if (debug_on):
        print("Port down request")
        debug_printer.pprint(data)
    return data


def generateMac(parent_mac, random_octet, debug=False):
    if debug:
        print("************ random_octet: %s **************" % (random_octet))
    my_oct = random_octet
    if (len(random_octet) == 4):
        my_oct = random_octet[2:]
    octets = parent_mac.split(":")
    octets[4] = my_oct
    return ":".join(octets)


def portNameSeries(prefix_="sta", start_id_=0, end_id_=1, padding_number_=10000):
    """
    This produces a named series similar to "sta000, sta001, sta002...sta0(end_id)"
    the padding_number is added to the start and end numbers and the resulting sum
    has the first digit trimmed, so f(0, 1, 10000) => {"0000", "0001"}
    @deprecated -- please use port_name_series
    :param prefix_:
    :param start_id_:
    :param end_id_:
    :param padding_number_:
    :return:
    """
    return port_name_series(prefix=prefix_, start_id=start_id_, end_id=end_id_, padding_number=padding_number_)


def port_name_series(prefix="sta", start_id=0, end_id=1, padding_number=10000):
    """
    This produces a named series similar to "sta000, sta001, sta002...sta0(end_id)"
    the padding_number is added to the start and end numbers and the resulting sum
    has the first digit trimmed, so f(0, 1, 10000) => {"0000", "0001"}
    @deprecated -- please use port_name_series
    :param prefix_: defaults to 'sta'
    :param start_id_: beginning id
    :param end_id_: ending_id
    :param padding_number_: used for width of resulting station number
    :return: list of stations
    """
    name_list = []
    for i in range((padding_number + start_id), (padding_number + end_id + 1)):
        sta_name = prefix + str(i)[1:]
        name_list.append(sta_name)
    return name_list


# generate random hex if you need it for mac addresses
def generateRandomHex():
    # generate a few random numbers and convert them into hex:
    random_hex = []
    for rn in range(0, 254):
        random_dec = randint(0, 254)
        random_hex.append(hex(random_dec))
    return random_hex


# return reverse map of aliases to port records
#
# expect nested records, which is an artifact of some ORM
# that other customers expect:
# [
#   {
#       "1.1.eth0": {
#           "alias":"eth0"
#       }
#   },
#   { ... }
def portListToAliasMap(json_list, debug_=False):
    reverse_map = {}
    if (json_list is None) or (len(json_list) < 1):
        if debug_:
            print("portListToAliasMap: no json_list provided")
            raise ValueError("portListToAliasMap: no json_list provided")
        return reverse_map

    json_interfaces = json_list
    if 'interfaces' in json_list:
        json_interfaces = json_list['interfaces']

    for record in json_interfaces:
        if len(record.keys()) < 1:
            continue
        record_keys = record.keys()
        k2 = ""
        # we expect one key in record keys, but we can't expect [0] to be populated
        json_entry = None
        for k in record_keys:
            k2 = k
            json_entry = record[k]
        # skip uninitialized port records
        if k2.find("Unknown") >= 0:
            continue
        port_json = record[k2]
        reverse_map[k2] = json_entry

    return reverse_map


def findPortEids(resource_id=1, base_url="http://localhost:8080", port_names=(), debug=False):
    port_eids = []
    if len(port_names) < 0:
        return []
    port_url = "/port/1"
    for port_name in port_names:
        uri = "%s/%s/%s" % (port_url, resource_id, port_name)
        lf_r = LFRequest.LFRequest(base_url, uri)
        try:
            response = lf_r.getAsJson(debug)
            if response is None:
                continue
            port_eids.append(PortEID(response))
        except:
            print("Not found: " + port_name)
    return port_eids


def waitUntilPortsAdminDown(resource_id=1, base_url="http://localhost:8080", port_list=()):
    print("Waiting until ports appear admin-down...")
    up_stations = port_list.copy()
    sleep(1)
    port_url = "/port/1"
    while len(up_stations) > 0:
        up_stations = []
        for port_name in port_list:
            uri = "%s/%s/%s?fields=device,down" % (port_url, resource_id, port_name)
            lf_r = LFRequest.LFRequest(base_url, uri)
            json_response = lf_r.getAsJson(debug_=False)
            if json_response == None:
                print("port %s disappeared" % port_name)
                continue
            if "interface" in json_response:
                json_response = json_response['interface']
            if json_response['down'] == "false":
                up_stations.append(port_name)
        sleep(1)
    return None


def waitUntilPortsAdminUp(resource_id=1, base_url="http://localhost:8080", port_list=()):
    return wait_until_ports_admin_up(resource_id=resource_id, base_url=base_url, port_list=port_list)

def wait_until_ports_admin_up(resource_id=1, base_url="http://localhost:8080", port_list=()):
    print("Waiting until  ports appear admin-up...")
    down_stations = port_list.copy()
    sleep(1)
    port_url = "/port/1"
    # url = /%s/%s?fields=device,down" % (resource_id, port_name)
    while len(down_stations) > 0:
        down_stations = []
        for port_name in port_list:
            uri = "%s/%s/%s?fields=device,down" % (port_url, resource_id, port_name)
            lf_r = LFRequest.LFRequest(base_url, uri)
            json_response = lf_r.getAsJson(debug_=False)
            if json_response == None:
                print("port %s appeared" % port_name)
                continue
            if "interface" in json_response:
                json_response = json_response['interface']
            if json_response['down'] == "true":
                down_stations.append(port_name)
        sleep(1)
    return None

def waitUntilPortsDisappear(resource_id=1, base_url="http://localhost:8080", port_list=[], debug=False):
    wait_until_ports_disappear(resource_id, base_url, port_list, debug)

def wait_until_ports_disappear(resource_id=1, base_url="http://localhost:8080", port_list=[], debug=False):
    print("Waiting until ports disappear...")
    url = "/port/1"
    found_stations = port_list.copy()
    sleep(1)
    while len(found_stations) > 0:
        found_stations = []
        sleep(1)
        for port_name in port_list:
            check_url = "%s/%s/%s" % (url, resource_id, port_name)
            if debug:
                print("checking:" + check_url)
            lf_r = LFRequest.LFRequest(base_url, check_url)
            json_response = lf_r.getAsJson(debug_=debug)
            if (json_response != None):
                found_stations.append(port_name)
    return


def waitUntilPortsAppear(base_url="http://localhost:8080", port_list=(), debug=False):
    """
    Deprecated
    :param resource_id:
    :param base_url:
    :param port_list:
    :param debug:
    :return:
    """
    return wait_until_ports_appear(base_url, port_list, debug=debug)

def name_to_eid(eid):
    rv = [1, 1, ""];
    info = []
    if (eid is None) or (eid == ""):
        raise ValueError("name_to_eid wants eid like 1.1.sta0 but given[%s]" % eid)
    
    info = eid.split('.')
    if (len(info) == 1):
        rv[2] = info[0]; # just port name
    if len(info) == 2: # resource.port-name
        rv[1] = int(info[0])
        rv[2] = info[1]
    if len(info) == 3: # shelf.resource.port-name
        rv[0] = int(info[0])
        rv[1] = int(info[1])
        rv[2] = info[2]

    return rv;

def wait_until_ports_appear(base_url="http://localhost:8080", port_list=(), debug=False):
    """

    :param base_url:
    :param port_list:
    :param debug:
    :return:
    """
    print("Waiting until ports appear...")
    found_stations = []
    port_url = "/port/1"
    ncshow_url = "/cli-form/nc_show_ports"
    if base_url.endswith('/'):
        port_url = port_url[1:]
        ncshow_url = ncshow_url[1:]

    while len(found_stations) < len(port_list):
        found_stations = []
        for port_eid in port_list:

            eid = name_to_eid(port_eid)
            shelf = eid[0]
            resource_id = eid[1]
            port_name = eid[2]
            
            uri = "%s/%s/%s" % (port_url, resource_id, port_name)
            lf_r = LFRequest.LFRequest(base_url, uri)
            json_response = lf_r.getAsJson(debug_=False)
            if (json_response != None):
                found_stations.append(port_name)
            else:
                lf_r = LFRequest.LFRequest(base_url, ncshow_url)
                lf_r.addPostData({"shelf": shelf, "resource": resource_id, "port": port_name, "flags": 1})
                lf_r.formPost()
        if (len(found_stations) < len(port_list)):
            sleep(2)

    if debug:
        print("These stations appeared: " + ", ".join(found_stations))
    return

def wait_until_endps(base_url="http://localhost:8080", endp_list=(), debug=False):
    """

    :param base_url:
    :param port_list:
    :param debug:
    :return:
    """
    print("Waiting until endpoints appear...")
    found_endps = []
    port_url = "/port/1"
    ncshow_url = "/cli-form/show_endp"
    if base_url.endswith('/'):
        port_url = port_url[1:]
        ncshow_url = ncshow_url[1:]

    while len(found_stations) < len(port_list):
        found_stations = []
        for port_eid in port_list:

            eid = name_to_eid(port_eid)
            shelf = eid[0]
            resource_id = eid[1]
            port_name = eid[2]
            
            uri = "%s/%s/%s" % (port_url, resource_id, port_name)
            lf_r = LFRequest.LFRequest(base_url, uri)
            json_response = lf_r.getAsJson(debug_=False)
            if (json_response != None):
                found_stations.append(port_name)
            else:
                lf_r = LFRequest.LFRequest(base_url, ncshow_url)
                lf_r.addPostData({"shelf": shelf, "resource": resource_id, "port": port_name, "flags": 1})
                lf_r.formPost()
        if (len(found_stations) < len(port_list)):
            sleep(2)

    if debug:
        print("These stations appeared: " + ", ".join(found_stations))
    return


def removePort(resource, port_name, baseurl="http://localhost:8080/", debug=False):
    if debug:
        print("Removing port %d.%s" % (resource, port_name))
    url = "/cli-json/rm_vlan"
    lf_r = LFRequest.LFRequest(baseurl, url)
    lf_r.addPostData({
        "shelf": 1,
        "resource": resource,
        "port": port_name
    })
    lf_r.jsonPost(debug)


def removeCX(baseurl, cx_names, debug=False):
    if debug:
        print("Removing cx %s" % ", ".join(cx_names))
    url = "/cli-json/rm_cx"
    for name in cx_names:
        data = {
            "test_mgr": "all",
            "cx_name": name
        }
        lf_r = LFRequest.LFRequest(baseurl, url)
        lf_r.addPostData(data)
        lf_r.jsonPost(debug)


def removeEndps(baseurl, endp_names, debug=False):
    if debug:
        print("Removing endp %s" % ", ".join(endp_names))
    url = "/cli-json/rm_endp"
    lf_r = LFRequest.LFRequest(baseurl, url)
    for name in endp_names:
        data = {
            "endp_name": name
        }
        lf_r.addPostData(data)
        lf_r.jsonPost(debug)


def execWrap(cmd):
    if os.system(cmd) != 0:
        print("\nError with '" + cmd + "', bye\n")
        exit(1)

###
