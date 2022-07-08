from functools import lru_cache

from wazo_sysconfd.plugins.asterisk.asterisk import Asterisk


@lru_cache()
def get_asterisk():
    return Asterisk()
