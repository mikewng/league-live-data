from typing import List
from app.core.config import Settings
import app.core.memory_data as memory
from openai import AsyncOpenAI

settings = Settings()

openai_api_key = settings.OPENAI_API_KEY
openai_model = settings.OPENAI_MODEL

openai_client = AsyncOpenAI(api_key=openai_api_key)

# System prompt for the League of Legends commentary agent
LEAGUE_AGENT_SYSTEM_PROMPT = (
    "You are a game stats agent for League of Legends that is very mean, and you will be given live game stats data of a match. "
    "Go out of your way to roast and criticize the player whenever you get the chance to, but still give good advice. "
    "Keep your responses concise and punchy - 2-3 sentences max. Focus on the most important aspects of what just happened."
)

async def run_agent_prompt(prompt: str) -> str:
    """Run OpenAI chat completion for League commentary"""
    if not prompt:
        return "I am at a loss for words. You just suck."

    try:
        response = await openai_client.chat.completions.create(
            model=openai_model,
            messages=[
                {"role": "system", "content": LEAGUE_AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.9
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "Error generating commentary. But honestly, you're probably doing terribly anyway."


async def text_to_speech(text: str, voice: str = "onyx") -> bytes:
    try:
        response = await openai_client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            response_format="mp3"
        )

        return response.content
    except Exception as e:
        print(f"Error generating speech: {e}")
        raise


async def handle_game_changes(changes: List) -> None:
    from app.services.change_detection_service import ChangeEvent, ChangeType
    from app.core.websocket_manager import ws_manager

    if not changes:
        return

    significant_changes = []
    for change in changes:
        if change.context.get("is_main_player", False):
            if change.change_type in [
                ChangeType.KILL,
                ChangeType.DEATH,
                ChangeType.ITEM_PURCHASE,
                ChangeType.GOLD_MILESTONE,
                ChangeType.CS_MILESTONE
            ]:
                significant_changes.append(change)
        elif change.change_type in [ChangeType.KILL, ChangeType.DEATH]:
            significant_changes.append(change)

    if not significant_changes:
        return

    prompts = [change.to_prompt() for change in significant_changes]
    combined_prompt = "\n".join(prompts)

    full_prompt = (
        f"The following events just happened in the game:\n\n"
        f"{combined_prompt}\n\n"
        f"Give a brief, snarky commentary on what just happened. Prioritizing on suggesting item builds for the active player and their champion:\n\n"
        f"Active Player's Username: {memory.game_data.main_player.name}\n\n"
        f"Active Player's Champion: {memory.game_data.main_player.champion}\n\n"
        f"Current Items: {memory.game_data.main_player.current_items}"
        f"Enemy Champions: {[enemy.name for enemy in memory.game_data.enemy_players]}"
        f"Be mean but helpful. Keep it short and punchy."
    )

    try:
        response = await run_agent_prompt(full_prompt)

        print(f"\n{'='*60}")
        print(f"AI AGENT RESPONSE:")
        print(f"{response}")
        print(f"{'='*60}\n")

        # Generate TTS audio
        audio_content = await text_to_speech(response, voice="onyx")

        # Send TTS event with audio to Discord bot via WebSocket
        await ws_manager.broadcast_tts_event(text=response, audio_content=audio_content, voice="onyx")

        return response
    except Exception as e:
        print(f"Error running AI agent on game changes: {e}")
        return None