from typing import Hashable, Any
from datetime import timedelta, datetime


class UnifiedDict(dict):
    objects = {}
    default_ttl = timedelta(days=1)

    def __init__(self, name: str, ttl: int | None = None, *args, **kwargs):
        self.ttl = ttl if ttl else self.default_ttl
        self.keys_with_dt = {}
        super().__init__(self, *args, **kwargs)

    def __new__(cls, name: str, ttl: int | None = None, *args, **kwargs):
        try:
            cls.objects[name]
        except KeyError:
            cls.objects[name] = super().__new__(cls)
        return cls.objects[name]

    def __setitem__(self, key: Hashable, value: Any) -> None:
        self.keys_with_dt[key] = datetime.now()
        super().__setitem__(key, value)

    def __getitem__(self, key: Hashable) -> Any:
        self._cleanup()
        return super().__getitem__(key)

    def _cleanup(self) -> None:
        keys = [
            item[0]
            for item in self.keys_with_dt.items()
            if item[1] + self.ttl < datetime.now()
        ]
        for key in keys:
            del self.keys_with_dt[key]
            self.__delitem__(key)
