import asyncio
import json
import os

from agent.clients.custom_mcp_client import CustomMCPClient
from agent.clients.mcp_client import MCPClient
from agent.clients.dial_client import DialClient
from agent.models.message import Message, Role


async def main():
    #TODO:
    # 1. Take a look what applies DialClient
    # 2. Create empty list where you save tools from MCP Servers later
    # 3. Create empty dict where where key is str (tool name) and value is instance of MCPClient or CustomMCPClient
    # 4. Create UMS MCPClient, url is `http://localhost:8006/mcp` (use static method create and don't forget that its async)
    # 5. Collect tools and dict [tool name, mcp client]
    # 6. Do steps 4 and 5 for `https://remote.mcpservers.org/fetch/mcp`
    # 7. Create DialClient, endpoint is `https://ai-proxy.lab.epam.com`
    # 8. Create array with Messages and add there System message with simple instructions for LLM that it should help to handle user request
    # 9. Create simple console chat (as we done in previous tasks)
    tools = []
    tool_clients = {}
    ums_mcp_client = await MCPClient.create(mcp_server_url="http://localhost:8006/mcp")
    ums_tools = await ums_mcp_client.get_tools()
    for tool in ums_tools:
        tools.append(tool)
        tool_clients[tool["function"]["name"]] = ums_mcp_client

    remote_mcp_client = await CustomMCPClient.create(mcp_server_url="https://remote.mcpservers.org/fetch/mcp")
    remote_tools = await remote_mcp_client.get_tools()
    for tool in remote_tools:
        tools.append(tool)
        tool_clients[tool["function"]["name"]] = remote_mcp_client

    dial_client = DialClient(endpoint="https://ai-proxy.lab.epam.com", api_key=os.getenv("DIAL_API_KEY"), tools=tools, tool_name_client_map=tool_clients)

    messages = [
        Message(
            role=Role.SYSTEM,
            content="You are an advanced AI agent. Your goal is to assist user with his questions."
        )
    ]

    while True:
        user_input = input("User: ")
        if user_input in {"exit", "quit"}:
            # delete mcp sessions before exit
            
            break

        messages.append(Message(role=Role.USER, content=user_input))

        response_message = await dial_client.get_completion(messages)
        messages.append(response_message)

if __name__ == "__main__":
    asyncio.run(main())


# Check if Arkadiy Dobkin present as a user, if not then search info about him in the web and add him