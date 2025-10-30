from typing import List
import os
from app.core.config import Settings
import app.core.memory_data as memory

settings = Settings()

openai_api_key = settings.OPENAI_API_KEY
openai_model = settings.OPENAI_MODEL

os.environ["OPENAI_API_KEY"] = openai_api_key

from agents import Agent, Runner

league_game_agent = Agent(
    name="League of Legends Game Agent",
    instructions=
        "You are a game stats agent for League of Legends that is very mean, and you will be given live game stats data of a match. " \
        "Go out of your way to roast and criticize the player whenever you get the chance to, but still give good advice. Use your given tools when appropriate. " \
        "Keep your responses concise and punchy - 2-3 sentences max. Focus on the most important aspects of what just happened.",
    model=openai_model,
)

async def run_agent_prompt(prompt: str) -> str:
    if (prompt is None or prompt == ""):
        return "I am at a lost for words. You just suck."

    result = await Runner.run(league_game_agent, prompt)
    return result.final_output


async def handle_game_changes(changes: List) -> None:
    from app.services.change_detection_service import ChangeEvent, ChangeType

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
        f"Active Player's Champion: {memory.game_data.main_player.champion}"
        f"Give a brief, snarky commentary on what just happened. Prioritizing on suggesting item builds for that champion."
        f"Be mean but helpful. Keep it short and punchy."
    )

    try:
        response = await run_agent_prompt(full_prompt)

        print(f"\n{'='*60}")
        print(f"AI AGENT RESPONSE:")
        print(f"{response}")
        print(f"{'='*60}\n")

        return response
    except Exception as e:
        print(f"Error running AI agent on game changes: {e}")
        return None