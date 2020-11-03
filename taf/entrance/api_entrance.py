from ..utils import typeassert


def _init_test_obj(module_name, cls_name, *args, **kwargs):
    module = __import__('src.objects.api.' + module_name, fromlist=[''])  # 'fromlist' arg is not an empty list
    return getattr(module, cls_name)(*args, **kwargs)


@typeassert(soap=bool, xml=bool, xml_args=dict)
def dispatch_request(module_name, cls_name, soap=False, xml=False, xml_args=None, *args, **kwargs):
    api_obj = _init_test_obj(module_name, cls_name, *args, **kwargs)

    if soap:
        api_obj.construct_xml(True, **xml_args)
    else:
        if xml:
            api_obj.construct_xml(False, **xml_args)
        else:
            api_obj.unflatten_json()
