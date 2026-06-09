from langchain.agents import create_agent
import os
from dotenv import load_dotenv
import getpass
from langchain_tavily import TavilySearch
from langchain_core.output_parsers import StrOutputParser


# if not os.environ.get("TAVILY_API_KEY"):
#     os.environ["TAVILY_API_KEY"] = getpass.getpass("Tavily API key:\n")

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

tavily_search_news_tool = TavilySearch(
    max_results=5,
    topic="news",
    time_range="week",
)

news_agent = create_agent(
    model="openai:gpt-5.4",
    tools=[tavily_search_news_tool],
    system_prompt="You are a helpful assistant",
)

result = news_agent.invoke({
    "messages": [{"role": "user", "content": "Give me the latest stock news for APPL"}]
})

print(result)
