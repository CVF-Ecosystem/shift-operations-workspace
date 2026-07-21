import asyncio
import logging
logging.basicConfig(level=logging.INFO)

async def run():
    logging.info("workspace-worker started in contract-safe skeleton mode")
    while True:
        await asyncio.sleep(30)
        logging.info("worker heartbeat")

if __name__ == "__main__":
    asyncio.run(run())
