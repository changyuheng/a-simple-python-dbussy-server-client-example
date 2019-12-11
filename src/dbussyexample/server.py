import asyncio
import logging
import os

import dbussy
import ravel


@ravel.interface(ravel.INTERFACE.SERVER, name='com.example.math')
class MathDBusServer:
    @ravel.method(
        name='Add',
        in_signature=(dbussy.BasicType(dbussy.TYPE.INT32), dbussy.BasicType(dbussy.TYPE.INT32)),
        out_signature=dbussy.BasicType(dbussy.TYPE.INT64),
        arg_keys=('a', 'b'))
    def add(self, a, b):
        logging.info('add({}, {})'.format(a, b))
        return [a + b]

    @ravel.method(
        name='Subtract',
        in_signature=(dbussy.BasicType(dbussy.TYPE.INT32), dbussy.BasicType(dbussy.TYPE.INT32)),
        out_signature=dbussy.BasicType(dbussy.TYPE.INT64),
        arg_keys=('a', 'b'))
    def subtract(self, a, b):
        logging.info('subtract({}, {})'.format(a, b))
        return [a - b]


def main():
    loop = asyncio.get_event_loop()

    bus = ravel.session_bus()
    bus.attach_asyncio(asyncio.get_event_loop())
    bus.request_name(bus_name='com.example.math', flags=0)
    bus.register(path='/com/example/math', fallback=True, interface=MathDBusServer())

    logging.info('starts serving...')
    loop.run_forever()
    return os.EX_OK
