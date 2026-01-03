import httpx
from httpx_sse import connect_sse, aconnect_sse
import asyncio

thread_id = "12334"
endpoint = f"http://localhost:8000/api/chat/ws/{thread_id}"


# with httpx.Client() as client:
#     with connect_sse(client, "POST", endpoint, json={"query": "Hello, how are you?"}) as event_source:
#         event_source.response.raise_for_status()
#         print(event_source.response.status_code)
#         for sse in event_source.iter_sse():
#             print(sse.event, sse.data, sse.id, sse.retry)
#             print(sse)

async def main():
    async with httpx.AsyncClient() as client:
        async with aconnect_sse(client, "POST", endpoint, json={"query": "Hello, how are you?"}) as event_source:
            event_source.response.raise_for_status()
            async for sse in event_source.aiter_sse():
                print(sse.event, sse.data)

if __name__ == "__main__":
    asyncio.run(main())