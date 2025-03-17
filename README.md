# livekit_Agent
livekit voice agent pipeline
# Voice Assistant Examples

We have a few examples that shows the various ways of using using the VoiceAssistant class:

- `minimal_assistant.py`: a basic conversational assistant
- `function_calling_weather.py`: a weather assistant that calls an API endpoint to retrieve the weather
- `custom_pronunciation.py`: using the `before_tts_cb` hook to customize how TTS pronounces words
- `simple_rag`: a simple RAG assistant that answers questions by querying a embeddings index

The demo assistants use:

- Deepgram for Speech-to-text
- OpenAI for LLM and Text-to-speech

## Run

Instructions for running the two agents are identical, the following steps will assume you are running `minimal_assistant.py`

### Setup and activate a virtual env:

`python -m venv venv`

`source venv/bin/activate`

### Set environment variables:

```bash
export LIVEKIT_URL=<LiveKit server URL>
export LIVEKIT_API_KEY=<API Key>
export LIVEKIT_API_SECRET=<API Secret>
export DEEPGRAM_API_KEY=<Deepgram API key>
export GROQ_API_KEY=<API key>
export CARTESIA_API_KEY=<API_KEY>
```

### Install requirments:

```
pip install -r requirements.txt
python minimal_assistant.py download-files
```

### Run the agent worker:

`python minimal_assistant.py dev`

### Test with a LiveKit frontend:

