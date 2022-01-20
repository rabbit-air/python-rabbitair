RabbitAir Python library
========================

This library can be used to control RabbitAir air purifiers over a local
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

        print("Set Speed to Low")
        await client.set_state(speed=Speed.Low)

        await asyncio.sleep(3)

        print("Set Mode to Auto")
        await client.set_state(mode=Mode.Auto)


asyncio.run(main())
```
