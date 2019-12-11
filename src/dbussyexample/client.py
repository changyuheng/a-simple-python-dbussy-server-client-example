import asyncio
import os
import random

import dbussy
import ravel


class DBusClient:
    def __init__(self, bus=None, shared=True, dest=None, path=None, iface=None, member=None):
        self._bus = bus
        self._shared = shared
        self._dest = dest
        self._path = path
        self._iface = iface
        self._member = member

        self._conn = None

    @property
    def bus(self):
        return self._bus

    @bus.setter
    def bus(self, value):
        self._bus = value

    @property
    def shared(self):
        return self._shared

    @shared.setter
    def shared(self, value):
        self._shared = value

    @property
    def dest(self):
        return self._dest

    @dest.setter
    def dest(self, value):
        self._dest = value

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def iface(self):
        return self._iface

    @iface.setter
    def iface(self, value):
        self._iface = value

    @property
    def member(self):
        return self._member

    @member.setter
    def member(self, value):
        self._member = value

    async def connect(self):
        if self._bus is None:
            raise ValueError('Bus type is missing.')
        return await dbussy.Connection.bus_get_async(self._bus, private=not self._shared)

    async def introspect_interface(self):
        if not self._conn:
            self._conn = await self.connect()

        message = dbussy.Message.new_method_call(
            destination=self._dest,
            path=self._path,
            iface=dbussy.DBUS.INTERFACE_INTROSPECTABLE,
            method='Introspect')

        reply = await self._conn.send_await_reply(message)
        introspection = dbussy.Introspection.parse(reply.expect_return_objects('s')[0])
        interfaces = introspection.interfaces_by_name

        if self._iface not in interfaces:
            raise RuntimeError('Bus peer {} object {} does not understand interface {}'.format(
                self._dest, self._path, self.iface))

        return interfaces.get(self._iface)


class DBusMethod(DBusClient):
    def __init__(self, bus=None, shared=True, dest=None, path=None, iface=None, member=None):
        super().__init__(bus=bus, shared=shared, dest=dest, path=path, iface=iface, member=member)

    async def introspect_method(self, *args):
        interface = await self.introspect_interface()

        methods = interface.methods_by_name
        if self._member not in methods:
            raise RuntimeError('Interface {} does not implement member {}'.format(
                self._iface, self._member))

        method = methods.get(self._member)

        message = dbussy.Message.new_method_call(
            destination=self._dest,
            path=self._path,
            iface=self._iface,
            method=self._member)

        signature = dbussy.parse_signature(method.in_signature)

        if len(signature) != len(args):
            raise RuntimeError('Wrong number of arguments, need: {}, got: {}'.format(
                len(signature), len(args)))

        if args:
            message.append_objects(signature, *args)
        else:
            message.append_objects(signature)

        return message

    async def call(self, *args):
        message = await self.introspect_method(*args)
        reply = await self._conn.send_await_reply(message)
        return reply.all_objects[0]


async def add(a, b):
    method = DBusMethod(
        bus=dbussy.DBUS.BUS_SESSION,
        shared=True,
        dest='com.example.math',
        path='/com/example/math',
        iface='com.example.math',
        member='Add')
    results = await method.call(a, b)
    return results


async def subtract(a, b):
    bus = ravel.session_bus()
    bus.attach_asyncio(asyncio.get_event_loop())
    iface = await bus.get_proxy_interface_async(
        destination='com.example.math',
        path='/com/example/math',
        interface='com.example.math')
    connection = iface(connection=bus.connection, dest='com.example.math')
    return (await connection['/com/example/math'].Subtract(a, b))[0]


async def example():
    a, b = random.randint(10, 100), random.randint(1, 10)
    print('[client] a = {}, b = {}'.format(a, b))

    print('[server] a + b = {}'.format(await add(a, b)))
    print('[server] a - b = {}'.format(await subtract(a, b)))


def main():
    asyncio.get_event_loop().run_until_complete(example())
    return os.EX_OK
