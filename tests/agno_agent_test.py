from typing import Any, Callable, Dict
from agno.utils.log import logger
from agno.agent import Agent
from agno.run.agent import RunOutput
from agno.models.ollama import Ollama
from agno.tools.websearch import WebSearchTools

def logger_hook(function_name: str, function_call: Callable, arguments: Dict[str, Any]):  
    logger.info(f"Running {function_name} with arguments {arguments}")  
    result = function_call(**arguments)  
    logger.info(f"Result of {function_name} is {result}")  
    return result  

def ask_agent(agent: Agent, question: str):
    response : RunOutput = agent.run(question)
    return response.content or ""

def main():
    agent = Agent(
        model=Ollama(id="gemma-ablitard-q6"),
        tools=[WebSearchTools()],
        instructions="Use the websearch tool to help answer user inquiries. max_results field of the websearch tool must be specified and an integer.",  
        tool_hooks=[logger_hook], 
        markdown=True,
    )
    print(ask_agent(agent,"who won 2026 soccor world cup?"))

if __name__ == "__main__":
    main()
