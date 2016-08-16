import argparse
import base64
import json
import urllib.request

USER_AGENT='telegraf-exec-eagle/1.0'

scale = { 'W': 1, 'kW': 1000 }

def get_usage_data_json(hostname, mac_id, username=None, password=None):
    '''
    Returns a dictionary like:
    {
      "demand": "4.1910",
      "demand_timestamp": "1471297512",
      "demand_units": "kW",
      "fast_poll_endtime": "0x00000000",
      "fast_poll_frequency": "0x00",
      "message_confirm_required": "N",
      "message_confirmed": "N",
      "message_id": "0",
      "message_queue": "active",
      "message_read": "Y",
      "message_timestamp": "946684800",
      "meter_status": "Connected",
      "price": "-1.0000",
      "price_units": "840",
      "summation_delivered": "52777.889",
      "summation_received": "0.000",
      "summation_units": "kWh",
      "threshold_lower_demand": "-2.000000",
      "threshold_upper_demand": "12.612000",
      "timezone_localTime": "1471297518",
      "timezone_olsonName": "America/Los_Angeles",
      "timezone_status": "success",
      "timezone_tzName": "PDT",
      "timezone_utcOffset": "-0700",
      "timezone_utcTime": "1471322718"
    }
    '''

    body = '''
<LocalCommand>
  <Name>get_timezone</Name>
  <MacId>{0!s}</MacId>
</LocalCommand>
<LocalCommand>
  <Name>get_usage_data</Name>
  <MacId>{0!s}</MacId>
</LocalCommand>
    '''.format(mac_id).strip()

    url = "http://{0}/cgi-bin/cgi_manager".format(hostname)

    headers = { "User-Agent": USER_AGENT }
    if username is not None and password is not None:
        auth = ("%s:%s" % (username, password)).encode()
        auth = base64.b64encode(auth).decode()
        headers["Authorization"] = 'Basic %s' % auth

    request = urllib.request.Request(url, body.encode(), headers)
    response = urllib.request.urlopen(request)
    charset = response.info().get_param('charset') or 'utf-8'
    body = response.read().decode(charset)
    return json.loads(body)

def format_influx_data(hostname, data):
    timezone_offset = int(data["timezone_utcTime"]) - int(data["timezone_localTime"])
    demand_timestamp = int(data["demand_timestamp"]) + timezone_offset
    demand = float(data["demand"]) * scale[data["demand_units"]]
    # TODO: also log price
    return "eagle,host=%s demand=%f %d000000000" % (hostname, demand, demand_timestamp)

parser = argparse.ArgumentParser(description='Get usage data from a Rainforest Eagle.')
parser.add_argument('hostname', metavar='HOSTNAME', type=str,
                   help='Hostname or IP of the Eagle')
parser.add_argument('mac', metavar='MAC', type=str,
                  help='MAC address of the Eagle\'s ZigBee radio')
parser.add_argument('--cloud-id', metavar='ID', type=str, default=None,
                   help='Eagle\'s Cloud ID')
parser.add_argument('--install-code', metavar='CODE', type=str, default=None,
                   help='Eagle\'s installer code')

args = parser.parse_args()

json = get_usage_data_json(args.hostname, args.mac, args.cloud_id, args.install_code)
print(format_influx_data(args.hostname, json))
