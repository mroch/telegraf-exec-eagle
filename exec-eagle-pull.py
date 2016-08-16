import argparse
import base64
import http.client
from utils import parse_demand, parse_price, parse_summation
from xml.etree import ElementTree

USER_AGENT='telegraf-exec-eagle/1.0'

def get_response(conn, command, mac, headers):
    body = '''
<Command>
    <Name>{0!s}</Name>
    <MacId>{1!s}</MacId>
</Command>
    '''.format(command, mac).strip()
    conn.request('POST', '/cgi-bin/post_manager', body, headers)
    response = conn.getresponse()
    charset = response.info().get_param('charset') or 'utf-8'
    return ElementTree.fromstring(response.read().decode(charset))

def print_demand(measurement, hostname, data):
    print((
        "{measurement:s},host={hostname:s},device={device:s},meter={meter:s},type=demand " +
        "value={demand:f} {timestamp:d}000000000"
    ).format(
        measurement=measurement,
        hostname=hostname,
        device=data['DeviceMacId'],
        meter=data['MeterMacId'],
        demand=data['Demand'],
        timestamp=data['TimeStamp'],
    ))

def print_summation(measurement, hostname, summation_data, price_data):
    print((
        "{measurement:s},host={hostname:s},device={device:s},meter={meter:s},type=summation " +
        "delivered={delivered:f},received={received:f},price={price:f},tier={tier:d} {timestamp:d}000000000"
    ).format(
        measurement=measurement,
        hostname=hostname,
        device=summation_data['DeviceMacId'],
        meter=summation_data['MeterMacId'],
        delivered=summation_data['SummationDelivered'],
        received=summation_data['SummationReceived'],
        price=price_data['Price'],
        tier=price_data['Tier'],
        timestamp=summation_data['TimeStamp'],
    ))

def print_data(hostname, mac, measurement, type, cloud_id=None, install_code=None):
    headers = { "User-Agent": USER_AGENT, 'Connection': 'keep-alive' }
    if cloud_id is not None and install_code is not None:
        auth = ("%s:%s" % (cloud_id, install_code)).encode()
        auth = base64.b64encode(auth).decode()
        headers["Authorization"] = 'Basic %s' % auth

    conn = http.client.HTTPConnection(hostname)
    if type == "demand":
        demand_xml = get_response(conn, "get_instantaneous_demand", mac, headers)
        demand = parse_demand(demand_xml)
        print_demand(measurement, hostname, demand)
    elif type == "summation":
        summation_xml = get_response(conn, "get_current_summation", mac, headers)
        price_xml = get_response(conn, "get_price", mac, headers)
        print_summation(
            measurement, hostname,
            parse_summation(summation_xml), parse_price(price_xml))

parser = argparse.ArgumentParser(description='Get usage data from a Rainforest Eagle.')
parser.add_argument('hostname', metavar='HOSTNAME', type=str,
                   help='Hostname or IP of the Eagle')
parser.add_argument('mac', metavar='MAC', type=str,
                  help='MAC address of the Eagle\'s ZigBee radio')
parser.add_argument('type', metavar='type', type=str, choices=['demand', 'summation'],
                   help='Data to fetch (demand or summation)')
parser.add_argument('--measurement', metavar='M', type=str, default='eagle',
                   help='InfluxDB measurement name')
parser.add_argument('--cloud-id', metavar='ID', type=str, default=None,
                   help='Eagle\'s Cloud ID')
parser.add_argument('--install-code', metavar='CODE', type=str, default=None,
                   help='Eagle\'s installer code')

args = parser.parse_args()
print_data(**vars(args))
