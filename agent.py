# --------------------------------------
# Imports and Environment Setup
# --------------------------------------

import asyncio
import warnings
import logging
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.tools.tool_context import ToolContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.agents.callback_context import CallbackContext
from google.genai import types # For creating response content
# Load environment variables (expects GOOGLE_API_KEY in .env)
from typing import Optional
load_dotenv()

# Silence warnings and unnecessary logs
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)

# --------------------------------------
# Constants
# --------------------------------------

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"
AGENT_MODEL = MODEL_GEMINI_2_0_FLASH

APP_NAME = "weather_tutorial_app"
USER_ID = "user_1"
SESSION_ID = "session_001"

USER_ID_STATEFUL = "user_state_demo"
SESSION_ID_STATEFUL = "session_state_demo_001"


# --------------------------------------
# Ensure Session Exists Before Running Test
# --------------------------------------

async def ensure_session_exists():
    print("\n--- Ensuring Session Exists ---")

    # Define initial state for the session
    initial_state = {
        "user_preference_temperature_unit": "Celsius"
    }

    # Attempt to create the session
    try:
        await session_service_stateful.create_session(
            app_name=APP_NAME,
            user_id=USER_ID_STATEFUL,
            session_id=SESSION_ID_STATEFUL,
            state=initial_state
        )
        print(f"✅ Session '{SESSION_ID_STATEFUL}' created for user '{USER_ID_STATEFUL}'.")
    except Exception as e:
        print(f"⚠️ Session might already exist or failed to create: {e}")


# --------------------------------------
# Weather Tool Definition
# --------------------------------------

def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """Retrieves weather, converts temp unit based on session state."""
    print(f"--- Tool: get_weather_stateful called for {city} ---")

    # --- Read preference from state ---
    preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius")  # Default to Celsius
    print(f"--- Tool: Reading state 'user_preference_temperature_unit': {preferred_unit} ---")

    city_normalized = city.lower().replace(" ", "")

    # Mock weather data (always stored in Celsius internally)
    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
    }

    if city_normalized in mock_weather_db:
        data = mock_weather_db[city_normalized]
        temp_c = data["temp_c"]
        condition = data["condition"]

        # Format temperature based on state preference
        if preferred_unit == "Fahrenheit":
            temp_value = (temp_c * 9 / 5) + 32  # Calculate Fahrenheit
            temp_unit = "°F"
        else:  # Default to Celsius
            temp_value = temp_c
            temp_unit = "°C"

        report = f"The weather in {city.capitalize()} is {condition} with a temperature of {temp_value:.0f}{temp_unit}."
        result = {"status": "success", "report": report}
        print(f"--- Tool: Generated report in {preferred_unit}. Result: {result} ---")

        # Example of writing back to state (optional for this tool)
        tool_context.state["last_city_checked_stateful"] = city
        print(f"--- Tool: Updated state 'last_city_checked_stateful': {city} ---")

        return result
    else:
        # Handle city not found
        error_msg = f"Sorry, I don't have weather information for '{city}'."
        print(f"--- Tool: City '{city}' not found. ---")
        return {"status": "error", "error_message": error_msg}

print("✅ State-aware 'get_weather_stateful' tool defined.")

# --------------------------------------
# Session and Runner Setup
# --------------------------------------

# Create the base InMemorySessionService (non-stateful session for earlier runner if needed)
session_service = InMemorySessionService()

# Create a separate stateful session service for stateful root agent and session
session_service_stateful = InMemorySessionService()
print("✅ New InMemorySessionService created for state demonstration.")

# --------------------------------------
# Tool Definition
# --------------------------------------

def say_goodbye() -> str:
    print(f"--- Tool: say_goodbye called ---")
    return "Goodbye! Have a great day."

def say_hello() -> str:
    print(f"--- Tool: say_hello called ---")
    return "Hello! How are you today."

# --------------------------------------
# Greeting Sub-Agent
# --------------------------------------

greeting_agent = None
try:
    # Use a defined model constant
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="greeting_agent", # Keep original name for consistency
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.",
        tools=[say_hello],
    )
    print(f"✅ Sub-Agent '{greeting_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Greeting agent. Check Model/API Key ({greeting_agent.model}). Error: {e}")

# --------------------------------------
# Farewell Sub-Agent
# --------------------------------------

farewell_agent = None
try:
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="farewell_agent",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools=[say_goodbye],
    )
    print(f"✅ Agent '{farewell_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Farewell agent. Error: {e}")

# --------------------------------------
# Guardrail Function
# --------------------------------------

def block_keyword_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Inspects the latest user message for 'BLOCK'. If found, blocks the LLM call
    and returns a predefined LlmResponse. Otherwise, returns None to proceed.
    """
    agent_name = callback_context.agent_name # Get the name of the agent whose model call is being intercepted
    print(f"--- Callback: block_keyword_guardrail running for agent: {agent_name} ---")

    # Extract the text from the latest user message in the request history
    last_user_message_text = ""
    if llm_request.contents:
        # Find the most recent message with role 'user'
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts:
                # Assuming text is in the first part for simplicity
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break # Found the last user message text

    print(f"--- Callback: Inspecting last user message: '{last_user_message_text[:100]}...' ---") # Log first 100 chars

    # --- Guardrail Logic ---
    keyword_to_block = "BLOCK"
    if keyword_to_block in last_user_message_text.upper(): # Case-insensitive check
        print(f"--- Callback: Found '{keyword_to_block}'. Blocking LLM call! ---")
        # Optionally, set a flag in state to record the block event
        callback_context.state["guardrail_block_keyword_triggered"] = True
        print(f"--- Callback: Set state 'guardrail_block_keyword_triggered': True ---")

        # Construct and return an LlmResponse to stop the flow and send this back instead
        return LlmResponse(
            content=types.Content(
                role="model", # Mimic a response from the agent's perspective
                parts=[types.Part(text=f"I cannot process this request because it contains the blocked keyword '{keyword_to_block}'.")],
            )
            # Note: You could also set an error_message field here if needed
        )
    else:
        # Keyword not found, allow the request to proceed to the LLM
        print(f"--- Callback: Keyword not found. Allowing LLM call for {agent_name}. ---")
        return None # Returning None signals ADK to continue normally

print("✅ block_keyword_guardrail function defined.")
# -----------------------------------------
# Define the Root Agent with Sub-Agents
# -----------------------------------------

root_agent_model_guardrail = None
runner_root_model_guardrail = None

# Check all components before proceeding
if greeting_agent and farewell_agent and 'get_weather_stateful' in globals() and 'block_keyword_guardrail' in globals():

    # Use a defined model constant
    root_agent_model = MODEL_GEMINI_2_0_FLASH

    root_agent_model_guardrail = Agent(
        name="weather_agent_v5_model_guardrail", # New version name for clarity
        model=root_agent_model,
        description="Main agent: Handles weather, delegates greetings/farewells, includes input keyword guardrail.",
        instruction="You are the main Weather Agent. Provide weather using 'get_weather_stateful'. "
                    "Delegate simple greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
                    "Handle only weather requests, greetings, and farewells.",
        tools=[get_weather_stateful],
        sub_agents=[greeting_agent, farewell_agent], # Reference the redefined sub-agents
        output_key="last_weather_report", # Keep output_key from Step 4
        before_model_callback=block_keyword_guardrail # <<< Assign the guardrail callback
    )
    print(f"✅ Root Agent '{root_agent_model_guardrail.name}' created with before_model_callback.")

    # --- Create Runner for this Agent, Using SAME Stateful Session Service ---
    # Ensure session_service_stateful exists from Step 4
    if 'session_service_stateful' in globals():
        runner_root_model_guardrail = Runner(
            agent=root_agent_model_guardrail,
            app_name=APP_NAME, # Use consistent APP_NAME
            session_service=session_service_stateful # <<< Use the service from Step 4
        )
        print(f"✅ Runner created for guardrail agent '{runner_root_model_guardrail.agent.name}', using stateful session service.")
    else:
        print("❌ Cannot create runner. 'session_service_stateful' from Step 4 is missing.")

else:
    print("❌ Cannot create root agent with model guardrail. One or more prerequisites are missing or failed initialization:")
    if not greeting_agent: print("   - Greeting Agent")
    if not farewell_agent: print("   - Farewell Agent")
    if 'get_weather_stateful' not in globals(): print("   - 'get_weather_stateful' tool")
    if 'block_keyword_guardrail' not in globals(): print("   - 'block_keyword_guardrail' callback")


# --------------------------------------
# Interaction Function
# --------------------------------------

async def call_agent_async(query: str, runner, user_id, session_id):
    print(f"\n>>> User Query: {query}")
    content = types.Content(role="user", parts=[types.Part(text=query)])
    final_response_text = "Agent did not produce a final response."

    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break

    print(f"<<< Agent Response: {final_response_text}")
# --------------------------------------
# Integrated Guardrail Interaction Test
# --------------------------------------

import asyncio  # Ensure asyncio is imported

# Ensure the runner exists
if 'runner_root_model_guardrail' in globals() and runner_root_model_guardrail:

    # Async conversation logic (defined globally)
    async def run_guardrail_test_conversation():
        print("\n--- Testing Model Input Guardrail ---")

        async def interaction_func(query: str):
            await call_agent_async(
                query=query,
                runner=runner_root_model_guardrail,
                user_id=USER_ID_STATEFUL,
                session_id=SESSION_ID_STATEFUL
            )

        print("--- Turn 1: Requesting weather in London (expect allowed, Fahrenheit) ---")
        await interaction_func("What is the weather in London?")

        print("\n--- Turn 2: Requesting with blocked keyword (expect blocked) ---")
        await interaction_func("BLOCK the request for weather in Tokyo")

        print("\n--- Turn 3: Sending a greeting (expect allowed) ---")
        await interaction_func("Hello again")

    # Async session state inspection
    async def inspect_final_guardrail_state():
        print("\n--- Inspecting Final Session State (After Guardrail Test) ---")
        final_session = await session_service_stateful.get_session(
            app_name=APP_NAME,
            user_id=USER_ID_STATEFUL,
            session_id=SESSION_ID_STATEFUL
        )

        if final_session:
            print(f"Guardrail Triggered Flag: {final_session.state.get('guardrail_block_keyword_triggered', 'Not Set')}")
            print(f"Last Weather Report: {final_session.state.get('last_weather_report', 'Not Set')}")
            print(f"Temperature Unit: {final_session.state.get('user_preference_temperature_unit', 'Not Set')}")
        else:
            print("❌ Error: Could not retrieve final session state.")

else:
    print("\n⚠️ Skipping guardrail test. Runner 'runner_root_model_guardrail' not available.")


runner = runner_root_model_guardrail
root_agent = root_agent_model_guardrail