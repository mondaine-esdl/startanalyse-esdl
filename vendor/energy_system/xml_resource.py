'''
Source
https://energytransition.gitbook.io/esdl/software-development/integration-with-python-and-pyecore
'''
import logging
from pyecore.resources.xmi import XMIResource, XMIOptions, XMI_URL, XSI_URL, XSI
from lxml.etree import QName, Element, ElementTree


logger = logging.getLogger(__name__)

"""
Extension of pyecore's XMIResource to support the XMLResource in EMF.
It basically removes the xmi:version stuff from the serialization.
"""
class XMLResource(XMIResource):
    def __init__(self, uri=None, use_uuid=False):
        super().__init__(uri, use_uuid)
        self._later = []
        self.prefixes = {}
        self.reverse_nsmap = {}
        self.parse_information = []

    def get_parse_information(self):
        return self.parse_information

    def save(self, output=None, options=None):
        self.options = options or {}
        output = self.open_out_stream(output)
        self.prefixes.clear()
        self.reverse_nsmap.clear()

        serialize_default = \
            self.options.get(XMIOptions.SERIALIZE_DEFAULT_VALUES,
                             False)
        nsmap = {XSI: XSI_URL} # remove XMI for XML serialization

        if len(self.contents) == 1:
            root = self.contents[0]
            self.register_eobject_epackage(root)
            tmp_xmi_root = self._go_across(root, serialize_default)
        else:
            # this case hasn't been verified for XML serialization
            tag = QName(XMI_URL, 'XMI')
            tmp_xmi_root = Element(tag)
            for root in self.contents:
                root_node = self._go_across(root, serialize_default)
                tmp_xmi_root.append(root_node)

        # update nsmap with prefixes register during the nodes creation
        nsmap.update(self.prefixes)
        xmi_root = Element(tmp_xmi_root.tag, nsmap=nsmap)
        xmi_root[:] = tmp_xmi_root[:]
        xmi_root.attrib.update(tmp_xmi_root.attrib)
        #xmi_version = etree.QName(XMI_URL, 'version') # remove XMI version in XML serialization
        #xmi_root.attrib[xmi_version] = '2.0'
        tree = ElementTree(xmi_root)
        tree.write(output,
                   pretty_print=True,
                   xml_declaration=True,
                   encoding=tree.docinfo.encoding)
        output.flush()
        return self.uri.close_stream()

    """
    This function has been overriden XMIResource, to make it a little more robust for ESDL's that
    are 'older' and do not have a certain feature. By default XMIResource throws an exception when
    an unknown attribute is found for a class. This version prints a warning and continues.
    """
    def _decode_attribute(self, owner, key, value):
        namespace, att_name = self.extract_namespace(key)
        prefix = self.reverse_nsmap[namespace] if namespace else None
        # This is a special case, we are working with uuids
        if key == self.xmiid:
            owner._internal_id = value
            self.uuid_dict[value] = owner
        elif prefix in ('xsi', 'xmi') and att_name == 'type':
            # type has already been handled
            pass
        # elif namespace:
        #     pass
        elif not namespace:
            if att_name == 'href':
                return
            feature = self._find_feature(owner.eClass, att_name)
            if not feature:
                #raise ValueError('Feature {0} does not exists for type {1}'
                #                 .format(att_name, owner.eClass.name))
                s = 'Attribute {0} does not exists for type {1} and is ignored.'.format(att_name, owner.eClass.name)
                logger.warning(s)
                self.parse_information.append(s)
            return feature