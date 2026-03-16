class UnifiedDict(dict):
    objects = {}

    def __new__(cls, *args, **kwargs):
        try:
            cls.objects[kwargs["name"]]
        except KeyError:
            cls.objects[kwargs["name"]] = super().__new__(cls)
        return cls.objects[kwargs["name"]]
