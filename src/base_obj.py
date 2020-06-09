import re

import lxml.etree as et


def set_attribute_for_node(ele, attr_dict):
    if attr_dict:
        for key, val in attr_dict.items():
            ele.set(key, val)


class BaseObject:
    rq_body = None
    soap_skin = None  # not overwriting if pure xml other than SOAP request

    def assemble_request_xml(self, rq_name, rq_dict, **root_attrs):
        root = et.Element(rq_name, **root_attrs)

        for key, value in rq_dict.items():
            cur_ele = root
            for node in key.split('.'):
                attr_dict = {}

                patt = r'(.*?)\((.*?)\)'
                match = re.search(patt, node)
                if bool(match):
                    kv_groups = match.group(2).split(',')
                    for kv in kv_groups:
                        kv = kv.strip()
                        attr_key, attr_val = kv.split('=')
                        attr_dict[attr_key.strip()] = attr_val.strip().replace('\'', '')
                    node = match.group(1)

                patt = r'(.*?)\[(.*?)\]'
                match = re.match(patt, node)
                if bool(match):
                    index = int(match.group(2))
                    node = match.group(1)
                    if len(cur_ele.findall('.//' + node)) == index:
                        sub_ele = et.SubElement(cur_ele, node)
                        set_attribute_for_node(sub_ele, attr_dict)
                        cur_ele = sub_ele
                    else:
                        cur_ele = cur_ele.findall('.//' + node)[index]
                elif cur_ele.find(node) is not None:
                    cur_ele = cur_ele.find(node)
                else:
                    sub_ele = et.SubElement(cur_ele, node)
                    set_attribute_for_node(sub_ele, attr_dict)
                    current_ele = sub_ele
            cur_ele.text = value

        self.rq_body = self.soap_skin % (et.tostring(root, encoding='unicode'))
