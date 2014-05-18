# coding: utf8

__author__ = 'breaker <breaker@broken.su>'

from construct import Adapter, Byte, Bytes, Struct, Switch, UBInt16, Pass, Enum, Const, Container as body
from binascii import unhexlify, hexlify


class RGBAdapter(Adapter):
    def _encode(self, obj, context):
        if obj.startswith("#"):
            val = obj[1:]
        else:
            val = obj
        return unhexlify(val)

    def _decode(self, obj, context):
        return "#%s" % ("".join(b.upper() for b in map(hexlify, obj)))


def RGB(name):
    return RGBAdapter(Bytes(name, 3))


cmd = Enum(Byte("cmd"),
        ON = 0x12,
        OFF = 0x13,
        COLOR = 0x20,
        #EXPLODE = 0x30,
        #STROB = 0x40,
        _default_ = Pass
    )

packet = Struct(
    "packet",
    cmd,
    Switch(
        "payload",
        lambda ctx: ctx.cmd,
        {
            "ON": Struct(
                "value",
                Const(UBInt16("length"), 0)
            ),
            "OFF": Struct(
                "value",
                Const(UBInt16("length"), 0)
            ),
            "COLOR": Struct(
                "value",
                UBInt16("length"),
                RGB("color"),
            ),
            #"EXPLODE": Pass,
            #"STROB": Struct(
                #"value",
                #UBInt16("length"),
                #Struct(
                    #"strobbing",
                    #Byte("delay"),
                    #Byte("count")
                #)
            #)
        },
    )
)
