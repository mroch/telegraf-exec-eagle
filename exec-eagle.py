import argparse
import http.server
import utils
from xml.etree import ElementTree

class EagleUploaderHandler(http.server.BaseHTTPRequestHandler):

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        length = int(self.headers.get('content-length'))
        data = self.rfile.read(length)
        root = ElementTree.fromstring(data)
        if root.tag != "rainforest":
            return # unexpected, so just drop the message
        child = root[0]

        if child.tag == "InstantaneousDemand":
            r = utils.parse_demand(child)
            print("eagle,type=demand,device={DeviceMacId:s},meter={MeterMacId:s} value={Demand:f} {TimeStamp:d}000000000".format(**r))

        elif child.tag == "CurrentSummationDelivered":
            r = utils.parse_summation(child)
            print ("eagle,type=summation,device={DeviceMacId:s},meter={MeterMacId:s} delivered={Delivered:f},received={Received:f} {TimeStamp:d}000000000".format(**r))

        elif child.tag == "PriceCluster":
            r = utils.parse_price(child)
            print("eagle,type=price,device={DeviceMacId:s},meter={MeterMacId:s} value={Price:f},tier={Tier:d} {TimeStamp:d}000000000".format(**r))

        elif child.tag == "DeviceInfo":
            r = utils.parse_device_info(child)
            return # ignore for now

        elif child.tag == "NetworkInfo":
            r = utils.parse_network_info(child)
            return # ignore for now

        elif child.tag == "MessageCluster":
            r = utils.parse_message(child)
            return # ignore for now

        elif child.tag == "TimeCluster":
            r = utils.parse_time(child)
            return # ignore for now

        elif child.tag == "ScheduleInfo":
            r = utils.parse_schedule(child)
            return # ignore for now

        elif child.tag == "BlockPriceDetail":
            r = utils.parse_block_price(child)
            return # ignore for now

        else:
            return # unknown request type

    def log_message(self, format, *args):
        return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get usage data from a Rainforest Eagle.')
    parser.add_argument('hostname', nargs='?', metavar='HOSTNAME', type=str,
                       help='Optional interface to listen on', default='')
    parser.add_argument('port', nargs='?', metavar='PORT', type=str,
                      help='Port to listen on', default='8080')
    args = parser.parse_args()

    httpd = http.server.HTTPServer((args.hostname, int(args.port)), EagleUploaderHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
