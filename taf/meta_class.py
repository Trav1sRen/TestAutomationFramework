class NotInstantiated(type):
    def __call__(cls, *args, **kwargs):
        """
        Control the instantiation of cls
        """
        raise TypeError('Cannot directly instantiate the base class ', cls.__name__)
