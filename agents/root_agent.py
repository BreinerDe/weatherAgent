from google.adk.agents import Agent
from tools.weather_tool import get_weather_stateful
from agents.greeting_agent import create_greeting_agent
from agents.farewell_agent import create_farewell_agent
from callbacks.guardrails import block_keyword_guardrail
from config import MODEL_GEMINI_2_0_FLASH

def create_root_agent():
    greeting_agent = create_greeting_agent()
    farewell_agent = create_farewell_agent()

    root_agent = Agent(
        name="weather_agent_v5_model_guardrail",
        model=MODEL_GEMINI_2_0_FLASH,
        description="Main agent: Handles weather, delegates greetings/farewells, includes input keyword guardrail.",
        instruction="You are the main Weather Agent. Provide weather using 'get_weather_stateful'. "
                    "Delegate simple greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
                    "Handle only weather requests, greetings, and farewells.",
        tools=[get_weather_stateful],
        sub_agents=[greeting_agent, farewell_agent],
        output_key="last_weather_report",
        before_model_callback=block_keyword_guardrail,
    )

    return root_agent
