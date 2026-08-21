# Voice Assistant Architecture Documentation

## Overview

This project implements a real-time voice assistant using the Pipecat framework. The architecture follows a pipeline-based design pattern where audio input flows through multiple processing stages: Speech-to-Text (STT) → Language Understanding/Tool Aggregation → Large Language Model (LLM) → Text-to-Speech (TTS).

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