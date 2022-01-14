RabbitAir Python library
========================

This library can be used to control RabbitAir air purifiers over a local
network.

# Usage

```python
#! /usr/bin/env python3

import asyncio
from rabbitair import UdpClient


async def main():
    with UdpClient("ip", "token") as client:
        response = await client.command({"cmd": 4})
        print(response)


asyncio.run(main())
```
