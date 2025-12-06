import asyncio
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

async def main():
    # Connect to remote MCP server
    async with MCPServerStreamableHttp(
        name="my-mcp-server",
        params={
            "url": "https://seven-icons-check.mcp.tadata.com/?tadata-api-key=tdk_494b7ad09c33a4d2cd6af32df86d92bdb1079e5406ed9712793842ca275e756e",
            "headers": {"Authorization": "Bearer "}
        }
    ) as remote_server:
        
        # Append to existing agent's mcp_servers
        agent = Agent(
            name="Assistant",
            instructions="Your instructions here",
            tools=[...],  # your existing tools
            mcp_servers=[remote_server]  # add remote server
        )
        
        result = await Runner.run(agent, "Your query here")
        print(result.final_output)

asyncio.run(main())