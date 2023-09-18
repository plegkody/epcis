import csv
from datetime import datetime, timedelta
import uuid
from xml.dom.minidom import parseString


sender_gln = "urn:epc:id:sgln:4030571.00000.0"
receiver_gln = "urn:epc:id:sgln:629500004013..0"

creation_date = "2019-01-01T00:00:00.000+00:00"
instance_identifier = "1234567890"

def get_current_time_in_epcis_format(ms=False):
    time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    if ms:
        time += ".000000"
    time += "Z"
    return time

def random_instance_identifier():
    # returns a random string , similar to 000D3AAA1A1B1EDE8CA3928358AC68C4
    return uuid.uuid4().hex.upper()

default_values = {
    'creation_date': get_current_time_in_epcis_format(ms=True),
    'instance_identifier': random_instance_identifier(),
    'first_event_time': get_current_time_in_epcis_format(),
    'event_time_zone': '+02:00',
}

epcis_template = """
<n0:EPCISDocument schemaVersion="1.1" creationDate="{creation_date}" xmlns:n0="urn:epcglobal:epcis:xsd:1" xmlns:prx="urn:sap.com:proxy:RSD:/1SAI/TASE5E38300795C1E3477C6:750" xmlns:n1="http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader">
{header}
{body}
</n0:EPCISDocument>
"""

header_template = """
	<EPCISHeader>
		<n1:StandardBusinessDocumentHeader>
			<n1:HeaderVersion>1.0</n1:HeaderVersion>
			<n1:Sender>
				<n1:Identifier Authority="SGLN">urn:epc:id:sgln:4030571.00000.0</n1:Identifier>
			</n1:Sender>
			<n1:Receiver>
				<n1:Identifier Authority="SGLN">urn:epc:id:sgln:629500004013..0</n1:Identifier>
			</n1:Receiver>
			<n1:DocumentIdentification>
				<n1:Standard>EPCglobal</n1:Standard>
				<n1:TypeVersion>1.0</n1:TypeVersion>
				<n1:InstanceIdentifier>{instance_identifier}</n1:InstanceIdentifier>
				<n1:Type>Events</n1:Type>
				<n1:CreationDateAndTime>{creation_date}</n1:CreationDateAndTime>
			</n1:DocumentIdentification>
		</n1:StandardBusinessDocumentHeader>
	</EPCISHeader>
"""

body_template = """
	<EPCISBody>
		<EventList>
			{events}
		</EventList>
	</EPCISBody>
"""

extension_qty_element_template = """
<extension>
        <quantityList>
            <quantityElement>
                <epcClass>{lgtin}</epcClass>
                <quantity>0</quantity>
            </quantityElement>
        </quantityList>
    </extension>
"""

commissioning_lgtin_template = """
<ObjectEvent>
    <eventTime>{event_time}</eventTime>
    <eventTimeZoneOffset>{event_time_zone}</eventTimeZoneOffset>
    <epcList/>
    <action>ADD</action>
    <bizStep>urn:epcglobal:cbv:bizstep:commissioning</bizStep>
    <disposition>urn:epcglobal:cbv:disp:active</disposition>
    <readPoint>
        <id>{read_point}</id>
    </readPoint>
    <bizLocation>
        <id>{biz_location}</id>
    </bizLocation>
    {extension_qty_element}
    <SAPExtension>
        <ObjAttributes>
            <LOTNO>{LOTNO}</LOTNO>
            <DATEX>{DATEX}</DATEX>
            <DATMF>{DATMF}</DATMF>
        </ObjAttributes>
    </SAPExtension>
</ObjectEvent>
"""

commissioning_sgtins_template = """
<ObjectEvent>
    <eventTime>{event_time}</eventTime>
    <eventTimeZoneOffset>{event_time_zone}</eventTimeZoneOffset>
    <epcList>
        {epc_list}
    </epcList>
    <action>ADD</action>
    <bizStep>urn:epcglobal:cbv:bizstep:commissioning</bizStep>
    <disposition>urn:epcglobal:cbv:disp:active</disposition>
    <readPoint>
        <id>{read_point}</id>
    </readPoint>
    <bizLocation>
        <id>{biz_location}</id>
    </bizLocation>
    <SAPExtension>
        <ObjAttributes>
            <LOTNO>{LOTNO}</LOTNO>
            <DATEX>{DATEX}</DATEX>
            <DATMF>{DATMF}</DATMF>
        </ObjAttributes>
    </SAPExtension>
</ObjectEvent>
"""

commissioning_ssccs_template = """
<ObjectEvent>
    <eventTime>{event_time}</eventTime>
    <eventTimeZoneOffset>{event_time_zone}</eventTimeZoneOffset>
    <epcList>
        {epc_list}
    </epcList>
    <action>ADD</action>
    <bizStep>urn:epcglobal:cbv:bizstep:commissioning</bizStep>
    <disposition>urn:epcglobal:cbv:disp:active</disposition>
    <readPoint>
        <id>{read_point}</id>
    </readPoint>
    <bizLocation>
        <id>{biz_location}</id>
    </bizLocation>
</ObjectEvent>
"""

packing_event_template = """
<AggregationEvent>
    <eventTime>{event_time}</eventTime>
    <eventTimeZoneOffset>{event_time_zone}</eventTimeZoneOffset>
    <parentID>{parent_id_epc}</parentID>
    <childEPCs>
        {epc_list}
    </childEPCs>
    <action>ADD</action>
    <bizStep>urn:epcglobal:cbv:bizstep:packing</bizStep>
    <readPoint>
        <id>{read_point}</id>
    </readPoint>
    <bizLocation>
        <id>{biz_location}</id>
    </bizLocation>
</AggregationEvent>
"""

bizTransaction_template = """<bizTransaction type="urn:epcglobal:cbv:btt:{bizTransaction_type}">{bizTransaction_GLN}:{bizTransaction_number}</bizTransaction>"""

source_owning_party_template = """<source type="urn:epcglobal:cbv:sdt:owning_party">{source_owning_party_GLN}</source>"""
source_location_template = """<source type="urn:epcglobal:cbv:sdt:location">{source_location_GLN}</source>"""
destination_owning_party_template = """<destination type="urn:epcglobal:cbv:sdt:owning_party">{destination_owning_party_GLN}</destination>"""
destination_location_template = """<destination type="urn:epcglobal:cbv:sdt:location">{destination_location_GLN}</destination>"""

shipping_event_template = """
<ObjectEvent>
    <eventTime>{event_time}</eventTime>
    <eventTimeZoneOffset>{event_time_zone}</eventTimeZoneOffset>
    <epcList>
        {epc_list}
    </epcList>
    <action>OBSERVE</action>
    <bizStep>urn:epcglobal:cbv:bizstep:shipping</bizStep>
    <disposition>urn:epcglobal:cbv:disp:in_transit</disposition>
    <readPoint>
        <id>{read_point}</id>
    </readPoint>
    <bizTransactionList>
        {bizTransactions}
    </bizTransactionList>
    <extension>
        <sourceList>
            {source_owning_party}
            {source_location}
        </sourceList>
        <destinationList>
            {destination_owning_party}
            {destination_location}
        </destinationList>
    </extension>
</ObjectEvent>
"""

def read_config():

    # read csv config file parameter;value and save to config dictionary
    config = {}
    with open('config.csv', mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            if len(row) >= 2:
                config[row[0]] = row[1]

    # replace DEFAULT values with values from default_values dictionary
    for key in config:
        # print(key, config[key])

        if config[key] == 'DEFAULT':
            config[key] = default_values[key]

    return config

def get_next_event_time(current_event_time, minutes_step=1, seconds_step=1):

    # event time is in format 2023-08-02T09:55:14Z
    # next event time is minutes_step minute later

    current_event_time = datetime.strptime(current_event_time, "%Y-%m-%dT%H:%M:%SZ")
    next_event_time = current_event_time + timedelta(minutes=minutes_step, seconds=seconds_step)
    return next_event_time.strftime("%Y-%m-%dT%H:%M:%SZ")

def read_sgtins_from_file():

    sgtins = []
    with open('sgtins.txt', mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            sgtins.append(row[0].strip())

    return sgtins

def get_epc_list(epcs):

    epc_list = ""
    for epc in epcs:
        epc_list += "<epc>{epc}</epc>\n".format(epc=epc)

    return epc_list

def generate_sscc_list(sscc_qty, sscc_template, last_sscc_id=None):
    # generates a list of ssccs of the format urn:epc:id:sscc:sscc_template.sscc_id
    # sscc_template example - sscc_template;urn:epc:id:sscc:4030571.2
    # resulting sscc is for example - urn:epc:id:sscc:4030571.2000003239
    # sscc_id should be incremental

    sscc_list = []

    if last_sscc_id is None:
        for i in range(1, sscc_qty + 1):  # Starting from 1 for a more natural ID
            padded_i = str(i).zfill(9)  # Padding to make it 10 digits long
            sscc_id = f"{sscc_template}{padded_i}"
            sscc_list.append(sscc_id)

    else:
        last_sscc_id = last_sscc_id.replace(sscc_template, '')
        last_sscc_id = int(last_sscc_id)

        for i in range(last_sscc_id + 1, last_sscc_id + sscc_qty + 1):
            padded_i = str(i).zfill(9)
            sscc_id = f"{sscc_template}{padded_i}"
            sscc_list.append(sscc_id)

    return sscc_list


def generate_packing_events_items_to_cases(cases_sscc_list, sgtins, config, current_event_time):

    packing_events = ""

    for case_sscc in cases_sscc_list:


        # get a list of sgtins for this case
        sgtins_for_this_case = sgtins[:int(config['hierarchy_items'])]

        # remove sgtins for this case from the sgtins list
        sgtins = sgtins[int(config['hierarchy_items']):]

        # generate a packing event for this case
        packing_event = packing_event_template.format(
            event_time=current_event_time,
            event_time_zone=config['event_time_zone'],
            parent_id_epc=case_sscc,
            epc_list=get_epc_list(sgtins_for_this_case),
            read_point=config['read_point'],
            biz_location=config['biz_location'])

        packing_events += packing_event

        current_event_time = get_next_event_time(current_event_time)

    return packing_events, current_event_time

def generate_packing_events_cases_to_pallets(pallets_sscc_list, cases_sscc_list, config, current_event_time):

    packing_events = ""

    for pallet_sscc in pallets_sscc_list:

        # get a list of cases for this pallet
        cases_for_this_pallet = cases_sscc_list[:int(config['hierarchy_cases'])]

        # remove cases for this pallet from the cases list
        cases_sscc_list = cases_sscc_list[int(config['hierarchy_cases']):]

        # generate a packing event for this pallet
        packing_event = packing_event_template.format(
            event_time=current_event_time,
            event_time_zone=config['event_time_zone'],
            parent_id_epc=pallet_sscc,
            epc_list=get_epc_list(cases_for_this_pallet),
            read_point=config['read_point'],
            biz_location=config['biz_location'])

        packing_events += packing_event

        current_event_time = get_next_event_time(current_event_time)

    return packing_events, current_event_time


def get_bizTransaction_if_defined(config, id):

    # config example
    # bizTransaction_type_1;sap_shp
    # bizTransaction_GLN_1;6295000040130
    # bizTransaction_number_1;SHP/MP/48913/2020

    bizTransaction = ""

    if config.get(f'bizTransaction_type_{id}') is not None:
        bizTransaction += bizTransaction_template.format(
            bizTransaction_type=config[f'bizTransaction_type_{id}'],
            bizTransaction_GLN=config[f'bizTransaction_GLN_{id}'],
            bizTransaction_number=config[f'bizTransaction_number_{id}'])

    return bizTransaction

def generate_shipping_event(pallets_sscc_list, config, current_event_time):

    # generate shipping event for all pallets together
    epc_list = get_epc_list(pallets_sscc_list)
    bizTransactions = get_bizTransaction_if_defined(config, 1)
    bizTransactions += get_bizTransaction_if_defined(config, 2)

    shipping_event = shipping_event_template.format(
        event_time=current_event_time,
        event_time_zone=config['event_time_zone'],
        epc_list=epc_list,
        read_point=config['read_point'],
        biz_location=config['biz_location'],
        bizTransactions=bizTransactions,
        source_owning_party=source_owning_party_template.format(**config),
        source_location=source_location_template.format(**config),
        destination_owning_party=destination_owning_party_template.format(**config),
        destination_location=destination_location_template.format(**config))

    return shipping_event

def beautify_xml(xml_string):
    dom = parseString(xml_string)
    return dom.toprettyxml()

if __name__ == '__main__':

    epcis_text = ""
    events_list = [
        'commissioning_lgtin',
        'commissioning_sgtins',
        'commissioning_ssccs',
        'packings',
        'shipping']

    config = read_config()

    # ================================ populate epcis header ===========================================

    header_text = header_template.format(**config)
    # header_text = header_text.replace('\n', '').replace('\t', '').replace(' ', '')

    # ================================ populate epcis body ===========================================

    current_event_time = config['first_event_time']
    last_sscc_id = None
    pallets_sscc_list = []
    cases_sscc_list = []
    total_number_items = int(config['hierarchy_items']) * int(config['hierarchy_cases']) * int(config['hierarchy_pallets'])

    sgtins = read_sgtins_from_file()

    event_time = current_event_time
    events_text = ""

    for event in events_list:

        if event == 'commissioning_lgtin':

            extension_qty_element = extension_qty_element_template.format(**config)
            event_text = commissioning_lgtin_template.format(**config, event_time=event_time, extension_qty_element=extension_qty_element)

        elif event == 'commissioning_sgtins':

            epcs = sgtins[:total_number_items]
            epc_list = get_epc_list(epcs)

            # hierarchy_items * hierarchy_cases * hierarchy_pallets = total_number_items
            event_text = commissioning_sgtins_template.format(**config, event_time=event_time, epc_list=epc_list)

        elif event == 'commissioning_ssccs':

            cases_sscc_list = generate_sscc_list(
                int(config['hierarchy_cases']) * int(config['hierarchy_pallets']),
                config['sscc_template'],
                last_sscc_id)

            last_sscc_id = cases_sscc_list[-1]

            pallets_sscc_list = generate_sscc_list(
                int(config['hierarchy_pallets']),
                config['sscc_template'],
                last_sscc_id)

            last_sscc_id = pallets_sscc_list[-1]

            event_text = commissioning_ssccs_template.format(**config, event_time=event_time, epc_list=get_epc_list(cases_sscc_list + pallets_sscc_list))

        elif event == 'packings':

            packing_events_items_to_cases, current_event_time = generate_packing_events_items_to_cases(cases_sscc_list, sgtins, config, current_event_time)
            packing_events_cases_to_pallets, current_event_time = generate_packing_events_cases_to_pallets(pallets_sscc_list, cases_sscc_list, config, current_event_time)
            event_text = packing_events_items_to_cases + packing_events_cases_to_pallets

        elif event == 'shipping':

            event_text = generate_shipping_event(pallets_sscc_list, config, current_event_time)

        # add current event to events_text
        events_text += event_text

        # get next event time
        event_time = get_next_event_time(current_event_time)
        current_event_time = event_time

    body = body_template.format(events=events_text)

    # ================================ populate epcis document ===========================================

    epcis_text = epcis_template.format(header=header_text, body=body, **config)
    epcis_text = beautify_xml(epcis_text)

    # get rid of empty lines
    epcis_text = '\n'.join([line for line in epcis_text.split('\n') if line.strip()])

    # save body to a result_epcis.txt file, re-write if exists
    with open('result_epcis.txt', mode='w') as result_file:
        result_file.write(epcis_text)
