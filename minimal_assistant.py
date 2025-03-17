import asyncio
import logging
import requests
from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm as lm,
    metrics,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import cartesia, deepgram, openai, silero


from livekit.plugins.openai import llm


load_dotenv()
logger = logging.getLogger("voice-assistant")

groq_llm = llm.LLM.with_groq(
  model="llama3-8b-8192",
  temperature=0.1,
)



def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    initial_ctx = lm.ChatContext().append(
        role="system",
        text=(
            "You are a voice assistant created by LiveKit. Your interface with users will be voice. "
            "You should use short and concise responses, and avoiding usage of unpronouncable punctuation."
        ),
    )
    #callback use to trim the content , if it exceeds more than 60 seconds
    def validate_text(text: str):
        response = requests.post(
            'https://9945-183-82-34-206.ngrok-free.app/validate-audio-length',
            json={'text': text}
        )
        
        if response.status_code == 200:
            return response.json().get('validated_text', text)  # Return validated text safely
        return text  # If API fails, return original text

    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")

    dg_model = "nova-3-general"
    if participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP:
        dg_model = "nova-2-phonecall"

    agent = VoicePipelineAgent(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(model=dg_model),
        llm=groq_llm,
        tts=cartesia.TTS(),
        chat_ctx=initial_ctx,
        before_tts_cb=lambda assistant, text: text,  #to call only once
    )

    agent.start(ctx.room, participant)

    usage_collector = metrics.UsageCollector()

    @agent.on("metrics_collected")
    def _on_metrics_collected(mtrcs: metrics.AgentMetrics):
        metrics.log_metrics(mtrcs)
        usage_collector.collect(mtrcs)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: ${summary}")

    ctx.add_shutdown_callback(log_usage)

    chat = rtc.ChatManager(ctx.room)

    async def answer_from_text(txt: str):
        chat_ctx = agent.chat_ctx.copy()
        chat_ctx.append(role="user", text=txt)

        response_text = ""
        async for chunk in agent.llm.chat(chat_ctx=chat_ctx):
            if chunk.choices and chunk.choices[0].delta.content:
                response_text += chunk.choices[0].delta.content  # Extract text correctly

        validated_text = validate_text(response_text)  # Call API only once
        await agent.say(validated_text)

    @chat.on("message_received")
    def on_chat_received(msg: rtc.ChatMessage):
        if msg.message:
            asyncio.create_task(answer_from_text(msg.message))

    await agent.say("Hey, how can I help you today?", allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
