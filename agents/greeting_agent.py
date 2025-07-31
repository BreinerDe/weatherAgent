from google.adk.agents import Agent
from tools.greetings import say_hello
from config import MODEL_GEMINI_2_0_FLASH

def create_greeting_agent() -> Agent:
    return Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="greeting_agent",
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.",
        tools=[say_hello],
    )
