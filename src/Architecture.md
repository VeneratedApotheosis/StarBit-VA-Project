# Voice Assistant Architecture Documentation

## Overview

This project implements a real-time voice assistant using the Pipecat framework. The architecture follows a pipeline-based design pattern where audio input flows through multiple processing stages: Speech-to-Text (STT) → Language Understanding/Tool Aggregation → Large Language Model (LLM) → Text-to-Speech (TTS).

## High-Level Architecture Diagram

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Audio In   │────▶│    VAD       │────▶│      STT      │────▶│      LLM      │────▶│      TTS      │
│             │     │ (Silero)     │     │ (Whisper)     │     │(Ollama/LLM)   │     │ (Piper)      │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       ▲                    │                      │                        │
       │                    ▼                      ▼                        ▼
    LocalAudioTransport  Context Aggregator   Tool Aggregator         Audio Output
```

## Project Structure

```
src/
├── __init__.py          # Package initialization (empty)
├── Architecture.md      # This documentation file
├── bot.py               # Main entry point - orchestrates the pipeline
├── config.py            # Configuration settings and constants
├── debug.py             # Debug utilities for logging frames
├── services.py          # Factory functions for creating service instances
└── tools.py             # Tool definitions for LLM function calling

models/
└── piper/               # Piper TTS model storage directory
```

## Component Breakdown

### 1. Configuration Layer (`config.py`)

The `Config` class serves as the single source of truth for all runtime configuration:

- **Language Settings**: Defines supported languages (EN, ZH) with mapping configurations for Whisper STT and Piper TTS voices
- **Whisper STT Settings**: Model selection (MEDIUM), device preference (CUDA/CPU), compute type
- **VAD Settings**: Silero VAD parameters including confidence threshold, start/stop seconds, minimum volume
- **LLM Settings**: Model identifier for Ollama integration
- **TTS Settings**: Piper model path and voice configuration
- **Audio Settings**: Sample rate (16kHz) for audio transport

### 2. Pipeline Orchestration (`bot.py`)

The `main()` function serves as the entry point that initializes and runs the complete pipeline:

**Pipeline Components:**
1. `LocalAudioTransport` - Handles local microphone input/output with configurable sample rates
2. `VADProcessor` - Voice Activity Detection using Silero model to detect speech boundaries
3. `WhisperSTTService` - Speech-to-Text conversion from audio to text
4. `LLMContextAggregatorPair` - Context aggregation that captures user speech turns
5. `OLLamaLLMService` - Large Language Model inference for response generation
6. `LLMResponsePrinter` - Debug utility that buffers and prints LLM responses
7. `PiperTTSService` - Text-to-Speech conversion from text to audio

**Observers:**
- `TranscriptionLogObserver`: Logs transcription frames for debugging
- `DebugLogObserver`: Logs VAD state changes (speech start/stop events)

### 3. Service Factory (`services.py`)

Centralized factory functions that create and configure service instances:

| Function | Returns | Purpose |
|----------|---------|---------|
| `create_stt_service()` | `WhisperSTTService` | Configures Whisper STT with language, model, device settings |
| `create_vad_analyzer()` | `SileroVADAnalyzer` | Configures Silero VAD with confidence and timing parameters |
| `create_llm_context()` | `LLMContext` | Initializes LLM context with system prompt and tools |
| `create_llm_aggregators()` | `LLMContextAggregatorPair` | Creates user/assistant aggregators for conversation state management |
| `create_llm_service()` | `OLLamaLLMService` | Configures Ollama LLM service with model selection |
| `create_tts_service()` | `PiperTTSService` | Configures Piper TTS with voice and CUDA settings |

### 4. Debug Utilities (`debug.py`)

Custom frame processors for debugging and logging:

- **TextPrinter**: Simple text frame printer (generic)
- **LLMResponsePrinter**: Buffers LLM response chunks and prints complete output when generation ends

### 5. Tool Definitions (`tools.py`)

Defines tools that the LLM can call via function calling:

| Tool | Parameters | Description |
|------|------------|-------------|
| `get_current_weather()` | location, format | Simulated weather API with async delay |
| `test_tool_1()` | None | Test tool for validation (returns "10012") |
| `test_tool_2()` | None | Test tool for validation (returns "50052") |

The `get_tools()` function returns the list of tools to inject into LLM context.

### 6. Models Directory (`models/piper/`)

Storage directory for Piper TTS models. Configured in `config.py` with default path `./models/piper`.

## Data Flow Sequence

1. **Audio Input**: User speaks into microphone → `LocalAudioTransport.input()`
2. **VAD Detection**: Audio passes through `VADProcessor` which uses Silero to detect speech boundaries
3. **Speech-to-Text**: Speech segments are converted to text by Whisper STT service
4. **Context Aggregation**: Text frames are aggregated into conversation context, tracking user/assistant turns
5. **LLM Inference**: Context is sent to LLM for response generation with tool capabilities
6. **Response Buffering**: `LLMResponsePrinter` buffers chunks and logs complete output when done
7. **Text-to-Speech**: Text responses are converted back to audio by Piper TTS service
8. **Audio Output**: Audio frames are sent through `LocalAudioTransport.output()`

## Key Design Patterns

### Pipeline Pattern
The core architecture uses Pipecat's pipeline pattern where data flows sequentially through processors, with each stage transforming the frame type appropriately (audio → text → context → response → audio).

### Observer Pattern
Observers (`TranscriptionLogObserver`, `DebugLogObserver`) are attached to the pipeline worker to capture specific frame types for logging and debugging.

### Factory Pattern
The `services.py` module uses factory functions to create properly configured service instances, ensuring consistent initialization across different environments.

### Context Aggregation
The `LLMContextAggregatorPair` manages conversation state by aggregating user speech into context while tracking assistant responses separately.

## Configuration Override

The project supports environment variable overrides via `.env` files using the `dotenv` library:

```python
load_dotenv(override=True)  # Loads .env with override flag
```

This allows runtime configuration changes without modifying code.

## Dependencies

Key external dependencies from Pipecat ecosystem:
- `pipecat.pipeline`: Core pipeline and worker infrastructure
- `pipecat.services.whisper.stt`: Whisper-based STT service
- `pipecat.services.piper.tts`: Piper-based TTS service
- `pipecat.audio.vad.silero`: Silero VAD for voice activity detection
- `pipecat.processors.aggregators.llm_context*: LLM context management

## Testing Structure

The project includes test files in the `tests/` directory:
- `agno_agent_test.py`: Tests for Agno-based agent implementation
- `bot_example.py`: Example bot usage patterns
- `pipecat_agent_test.py`: Pipecat agent integration tests
- `pipecat_stt_test.py`: STT service validation tests
- `stt_llm_test.py`: Combined STT+LLM flow tests
- `test_tts.py`: TTS service validation tests
