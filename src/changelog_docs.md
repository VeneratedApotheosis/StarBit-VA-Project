
## 8/18
### Current Issues
Agentic Thinking: Currently all models are run locally, including the LLM. High perplexity is required for agentic reasoning, which requires more parameters, which requires larger size models, which means hardware limitations.

Voice activation and STT: The second primary problem is accuracy of STT and voice activation. Accuracy is primarily an issue when multiple people speak at once, then the STT almost entirely fails to accurately transcribe audio. Voice activation also sometimes doens't trigger when it should, meaning thresholds should be lowered.

## 8/19 
Testing tools through voice commands takes too long, created a WS text based interactive bot, debugged testing program.
structured:
```
src/
├── client    # CL JS WS client connecting to server backend
└── server    # Python backend hosting the bot exposed through local WS
```

## 8/21
### tools
Created new file, http_utility, for better separation of concerns
API tool for getting weather:
    Requires two api calls if given location name, fetching coordinates of location (geocoding) -> fetching weather at coordinates.

two opts for impl:
    one tool, geociding --> coord weather,
    two tools, geocoding + coord weather:
        pro: more flexibility + slightly more features
        con: higher latency (two agentic loops) + higher hallucination 

    VA priority is latency and due to hardware limitations of running model, has real risk of hallucination, so impl one tool

Refactor code in http client, added fetch_json boilerplate, changed structure where flow is controlled by exceptions.
Refactor code in tools, added safe_tool decorator boilerplate, added exception handling.
Initial tool of 'get_time_tool' is added, works fine.
First API tool to implement is 'get_geocoding_tool', tool adapter is being tested.
There was an error in the initial tool adapter, where llm output is un-generated after api tool was called, debugging.
Issue was with frames, the wrong text frame was inputted. the llm service only recognizes a certain type of text frame. altering frame inputted fixed issue.

for api tools, domain payload extraction is in utility, while pruning happens in tools.
Implemented 'get_geocoding_tool' in full.
Implemented 'get_forecast_place_tool' basic functionality, gets current weather at a given location.

splitting forecasting into atleast two tools, getting current weather, and getting weather at a given range of dates.
Implemented 'get_current_forecast_tool' in full.

Implementing 'get_daily_forecast_tool' requires an additional utility  tool for fetching daily ranges of forecasts. original utility func cannot be generalized as shape of response json is diff.

daily forecasts returns a parallel array, normalizing into singular daily obj is required.
added more boilerplate for normalizing raw json responses. uses ZIP to unpack and reformat parallel arrays

new libraries used: aiohttp, aDDGS, ZIP

<!-- ----------------------------------------------------------------------- -->
<!--                               TOOL DESIGN                               -->
<!-- ----------------------------------------------------------------------- -->
Tools are implemented in 'utility.py' and 'tools.py'
flow is primarily controlled by exceptions. 

'tools.py': contains tool definition, which are exposed to the llm. 
- handles data pruning and post processing before handing to llm for parsing
- boilerplate 'safe_tools' decorator for all tool functions implementing exception and safety handling
- 'register_tools' exposes the function to the LLM.

all tools follow this design pattern:
```
@register_tool
@tool_options(cancel_on_interruption=False, timeout_secs=30)
@safe_tool
async def tool_name(params: FunctionCallParams, ...):
    """REQUIRED docstring describing function and args for llm comprehension"""
    
    # 1. utility call
    data = await utility.some_function(...)
    
    # 2. prune data
    pruned_data = prune(...)
    
    # 3. Return result to LLM
    await params.result_callback(result)
```

'utility.py': contains all logic for features implemented in tools.
- handling data normalization and formatting before being exposed to tools
- contains all logic for calling external APIs (Open-Meteo, DDGS)
- raises exceptions for control flow in tool.py
- utilizes 'http_client.py' which contains boilerplate code for using aiohttp.

utility contains logic and implementation, tools contains control flow and tool definitions.

IMPLEMENTED MARKDOWN FILTER