from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class Context7Manager:
    def __init__(self):
        self.session = None
        self.exit_stack = None

    async def connect(self):
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@upstash/context7-mcp"],
        )
        # stdio 연결 관리
        self.client_context = stdio_client(server_params)
        self.read, self.write = await self.client_context.__aenter__()
        self.session = ClientSession(self.read, self.write)
        await self.session.__aenter__()
        await self.session.initialize()

    async def search_docs(self, query: str) -> str:
        """라이브러리 문서를 검색합니다."""
        # 1. 라이브러리 ID 식별 (예: 'pandas')
        lib_res = await self.session.call_tool("resolve-library-id", {"libraryName": query})
        lib_id = lib_res.content[0].text
        
        # 2. 해당 라이브러리 문서 쿼리
        docs_res = await self.session.call_tool("query-docs", {"libraryId": lib_id, "query": "latest usage and best practices"})
        return docs_res.content[0].text

    async def close(self):
        await self.session.__aexit__(None, None, None)
        await self.client_context.__aexit__(None, None, None)