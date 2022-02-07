Rabbit Air Python library
=========================

This library can be used to control Rabbit Air air purifiers over a local
network.

# Usage

```python
#! /usr/bin/env python3

import asyncio

from rabbitair import Mode, Speed, UdpClient


async def main():
    with UdpClient("ip", "token") as client:

        # Getting the current state of the air purifier

        state = await client.get_state()
        print(state)

        # Controlling the air purifier

        print("Power Off")
        await client.set_state(power=False)

        await asyncio.sleep(3)

        print("Power On")
        await client.set_state(power=True)

        await asyncio.sleep(3)

        print("Set Speed to High")
        await client.set_state(speed=Speed.High)

        await asyncio.sleep(3)

        print("Set Mode to Auto")
        await client.set_state(mode=Mode.Auto)


asyncio.run(main())
```

# Retrieving the Access Token

To establish a connection, you need to know the address and access token of the
device.

1. Open the Rabbit Air mobile app. You will see a list of devices connected to
   your account.
2. Tap the list item and the device control page will open.
3. On the device page tap the `Edit` button. You will see a page with the
   device location and name settings.
4. On this page, quickly tap on "Serial Number" several times until you see two
   more lines that were previously hidden. The first is the device ID, and the
   second is the access token.

Note that the device ID is used as an mDNS name of the device. So you can
specify it as the `host` value by adding the suffix ".local" at the end.

For example, you got:

![Screenshot: Access token on the "Edit device" screen](https://raw.githubusercontent.com/rabbit-air/python-rabbitair/master/images/access_token.png)

Then you can use `abcdef1234_123456789012345678.local` as the `host` and
`0123456789ABCDEF0123456789ABCDEF` as the `token`.

In some cases the access token may not be available right away, then you will
see a "Tap for setup user key" message instead. To generate the access token,
tap on this message and follow the instructions. If the app says "your device
is not supported", it probably means that you are trying to connect to a
first-generation MinusA2 model (an older hardware revision). It is not yet
supported.
