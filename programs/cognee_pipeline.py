
import sys
import asyncio
from cognee.api.v1.config import config
from cognee.api.v1.cognify import cognify
from cognee.api.v1.search import search

async def main(query: str):
    # Configure cognee to use the local endpoint
    config.set_llm_provider("litellm")
    config.set_llm_model("ollama/minimax-m3")
    config.set_llm_api_key(None)
    config.set_llm_endpoint("http://localhost:20128")

    # 1. cognify the data
    await cognify("C:\\Users\\Mateusz\\Desktop\\Notes\\best you")
    # 2. search
    print(await search(query))

if __name__ == "__main__":
    # for now, let's just test with a hardcoded query
    asyncio.run(main("Jak siła woli się wyczerpuje i jak ją odnawiać?"))
