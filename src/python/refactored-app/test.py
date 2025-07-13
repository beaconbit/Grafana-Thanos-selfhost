import asyncio
import nats
import time

async def test():
    nc = await nats.connect("nats://localhost:4222")
    js = nc.jetstream()

    # Ensure stream exists (only once)
    try:
        await js.add_stream(name="TEST", subjects=["foo"])
    except:
        pass  # Stream might already exist

    # Now publish
    while True:
        ack = await js.publish("foo", b"hello")
        time.sleep(5)
        await nc.drain()

asyncio.run(test())


