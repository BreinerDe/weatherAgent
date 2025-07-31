from google.adk.agents import Agent
from tools.greetings import say_goodbye
from config import MODEL_GEMINI_2_0_FLASH

def create_farewell_agent() -> Agent:
    return Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="farewell_agent",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools=[say_goodbye],
    )
