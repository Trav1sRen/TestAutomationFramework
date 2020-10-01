class ApiEntrance:
    inst = None

    def init_test_obj(self, module_name, cls_name, *args, **kwargs):
        module = __import__('src.objects.api.' + module_name, fromlist=[''])  # 'fromlist' arg is not an empty list
        self.inst = getattr(module, cls_name)(*args, **kwargs)
