
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

