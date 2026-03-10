class UnifiedDict(dict):
    objects = {}

    def __new__(cls, name: str):
        try:
            cls.objects[name]
        except KeyError:
            cls.objects[name] = super().__new__(cls)
        return cls.objects[name]
