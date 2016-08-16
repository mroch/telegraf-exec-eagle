import re

from datetime import datetime

MAC_RE = re.compile(r'^(?:0x)?([0-9A-Za-z]{2})[:.-]?([0-9A-Za-z]{2})[:.-]?([0-9A-Za-z]{2})[:.-]?([0-9A-Za-z]{2})[:.-]?([0-9A-Za-z]{2})[:.-]?([0-9A-Za-z]{2})(?:[:.-]?([0-9A-Za-z]{2})[:.-]?([0-9A-Za-z]{2}))?')

def normalize_mac(mac):
    octets = MAC_RE.match(mac)
    if octets is None:
        return None
    return '-'.join(filter(None, octets.groups()))

def y2k_to_epoch_datetime(timestamp):
    return datetime.utcfromtimestamp(946684800 + timestamp)

def get_mac(elem, field):
    return normalize_mac(elem.find(field).text)

def get_datetime_y2k(elem, field):
    return y2k_to_epoch_datetime(int(elem.find(field).text, 16))

def get_watts(elem, field):
    value = int(elem.find(field).text, 16)
    multiplier = int(elem.find("Multiplier").text, 16) or 1
    divisor = int(elem.find("Divisor").text, 16) or 1
    return value * multiplier / divisor * 1000 # watts

def parse_demand(elem):
    """
    <InstantaneousDemand>
      <DeviceMacId>0xdeadbeef0000661a</DeviceMacId>
      <MeterMacId>0xdeadbeef00e33f60</MeterMacId>
      <TimeStamp>0x1f441da9</TimeStamp>
      <Demand>0x000b79</Demand>
      <Multiplier>0x00000001</Multiplier>
      <Divisor>0x000003e8</Divisor>
      <DigitsRight>0x03</DigitsRight>
      <DigitsLeft>0x0f</DigitsLeft>
      <SuppressLeadingZero>Y</SuppressLeadingZero>
      <Port>/dev/ttySP0</Port>
    </InstantaneousDemand>
    """
    eagle_zigbee_mac = get_mac(elem, "DeviceMacId")
    meter_zigbee_mac = get_mac(elem, "MeterMacId")
    reading_timestamp = get_datetime_y2k(elem, "TimeStamp")
    demand = get_watts(elem, "Demand")
    return {
        'DeviceMacId': eagle_zigbee_mac,
        'MeterMacId': meter_zigbee_mac,
        'Demand': demand,
        'TimeStamp': int(reading_timestamp.timestamp())
    }

def parse_price(elem):
    """
    <PriceCluster>
      <DeviceMacId>0xdeadbeef0000661a</DeviceMacId>
      <MeterMacId>0xdeadbeef00e33f60</MeterMacId>
      <TimeStamp>0xffffffff</TimeStamp>
      <Price>0xffffffff</Price>
      <Currency>0x0348</Currency>
      <TrailingDigits>0x0f</TrailingDigits>
      <Tier>0x00</Tier>
      <StartTime>0x00000000</StartTime>
      <Duration>0x0000</Duration>
      <RateLabel />
      <Port>/dev/ttySP0</Port>
    </PriceCluster>
    """
    eagle_zigbee_mac = get_mac(elem, "DeviceMacId")
    meter_zigbee_mac = get_mac(elem, "MeterMacId")
    reading_timestamp = get_datetime_y2k(elem, "TimeStamp")
    raw_price = int(elem.find('Price').text, 16)
    if raw_price == 0xffffffff:
        price = 0
    else:
        divisor = 10**(int(elem.find('TrailingDigits').text, 16)) or 1
        price = raw_price / divisor
    return {
        'DeviceMacId': eagle_zigbee_mac,
        'MeterMacId': meter_zigbee_mac,
        'TimeStamp': int(reading_timestamp.timestamp()),
        'Currency': int(elem.find('Currency').text, 16),
        'Tier': int(elem.find('Tier').text, 16),
        'Price': price,
    }

def parse_summation(elem):
    """
    <CurrentSummationDelivered>
      <DeviceMacId>0xdeadbeef0000661a</DeviceMacId>
      <MeterMacId>0xdeadbeef00e33f60</MeterMacId>
      <TimeStamp>0x1f442748</TimeStamp>
      <SummationDelivered>0x000000000324b034</SummationDelivered>
      <SummationReceived>0x0000000000000000</SummationReceived>
      <Multiplier>0x00000001</Multiplier>
      <Divisor>0x000003e8</Divisor>
      <DigitsRight>0x03</DigitsRight>
      <DigitsLeft>0x0f</DigitsLeft>
      <SuppressLeadingZero>Y</SuppressLeadingZero>
      <Port>/dev/ttySP0</Port>
    </CurrentSummationDelivered>
    """
    eagle_zigbee_mac = get_mac(elem, "DeviceMacId")
    meter_zigbee_mac = get_mac(elem, "MeterMacId")
    reading_timestamp = get_datetime_y2k(elem, "TimeStamp")
    delivered = get_watts(elem, "SummationDelivered")
    received = get_watts(elem, "SummationReceived")
    return {
        'DeviceMacId': eagle_zigbee_mac,
        'MeterMacId': meter_zigbee_mac,
        'TimeStamp': int(reading_timestamp.timestamp()),
        'SummationDelivered': delivered,
        'SummationReceived': received,
    }

def parse_device_info(elem):
    """
    <DeviceInfo>
      <DeviceMacId>0xdeadbeef0000661a</DeviceMacId>
      <InstallCode>0xdeadbeefdeadbeef</InstallCode>
      <LinkKey>0xabcdefabcdefabcdefabcdef012345678</LinkKey>
      <FWVersion>1.4.48 (6952)</FWVersion>
      <HWVersion>1.2.6</HWVersion>
      <ImageType>0x1301</ImageType>
      <Manufacturer>Rainforest Automation, Inc.</Manufacturer>
      <ModelId>Z109-EAGLE</ModelId>
      <DateCode>2015102225020857</DateCode>
      <Port>/dev/ttySP0</Port>
      <Port>/dev/ttySP0</Port>
    </DeviceInfo>
    """
    # TODO
    return {}

def parse_network_info(elem):
    """
    <NetworkInfo>
      <DeviceMacId>0xdeadbeef0000661a</DeviceMacId>
      <CoordMacId>0xdeadbeef00e33f60</CoordMacId>
      <Status>Connected</Status>
      <Description>Successfully Joined</Description>
      <ExtPanId>0xdeadbeef00e33f60</ExtPanId>
      <Channel>25</Channel>
      <ShortAddr>0x4249</ShortAddr>
      <LinkStrength>0x64</LinkStrength>
      <Port>/dev/ttySP0</Port>
    </NetworkInfo>
    """
    # TODO
    return {}

def parse_message(elem):
    """
    <MessageCluster>
      <DeviceMacId>0xdeadbeef0000661a</DeviceMacId>
      <MeterMacId>0xdeadbeef00e33f60</MeterMacId>
      <TimeStamp />
      <Id />
      <Text />
      <Priority />
      <StartTime />
      <Duration />
      <ConfirmationRequired>N</ConfirmationRequired>
      <Confirmed>N</Confirmed>
      <Queue>Active</Queue>
      <Port>/dev/ttySP0</Port>
    </MessageCluster>
    """
    # TODO
    return {}

def parse_time(elem):
    """
    <TimeCluster>
      <DeviceMacId>0xdeadbeef0000661a</DeviceMacId>
      <MeterMacId>0xdeadbeef00e33f60</MeterMacId>
      <UTCTime>0x1f4427cc</UTCTime>
      <LocalTime>0x1f43c55c</LocalTime>
      <Port>/dev/ttySP0</Port>
    </TimeCluster>
    """
    # TODO
    return {}

def parse_schedule(elem):
    """
    <ScheduleInfo>
      <DeviceMacId>0xdeadbeef0000661a</DeviceMacId>
      <MeterMacId>0xdeadbeef00e33f60</MeterMacId>
      <Mode>default</Mode>
      <Event>time | message | price | summation | demand | scheduled_prices | profile_data | billing_period | block_period</Event>
      <Frequency>0x00000384</Frequency>
      <Enabled>Y</Enabled>
      <Port>/dev/ttySP0</Port>
    </ScheduleInfo>
    """
    # TODO
    return {}

def parse_block_price(elem):
    """
    <BlockPriceDetail>
      <DeviceMacId>0xdeadbeef0000661a</DeviceMacId>
      <MeterMacId>0xdeadbeef00e33f60</MeterMacId>
      <TimeStamp>0x1f443084</TimeStamp>
      <CurrentStart>0x00000000</CurrentStart>
      <CurrentDuration>0x0000</CurrentDuration>
      <BlockPeriodConsumption>0x0000000000000000</BlockPeriodConsumption>
      <BlockPeriodConsumptionMultiplier>0x00000001</BlockPeriodConsumptionMultiplier>
      <BlockPeriodConsumptionDivisor>0x000003e8</BlockPeriodConsumptionDivisor>
      <NumberOfBlocks>0x00</NumberOfBlocks>
      <Multiplier>0x00000001</Multiplier>
      <Divisor>0x00000001</Divisor>
      <Currency>0x0348</Currency>
      <TrailingDigits>0x00</TrailingDigits>
      <Port>/dev/ttySP0</Port>
    </BlockPriceDetail>
    """
    # TODO
    return {}
