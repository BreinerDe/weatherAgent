from google.adk.sessions import InMemorySessionService

# Create sessions here, so they can be imported anywhere
session_service = InMemorySessionService()
session_service_stateful = InMemorySessionService()

APP_NAME = "weather_tutorial_app"
USER_ID_STATEFUL = "user_state_demo"
SESSION_ID_STATEFUL = "session_state_demo_001"

async def ensure_session_exists():
    print("\n--- Ensuring Session Exists ---")

    initial_state = {
        "user_preference_temperature_unit": "Celsius"
    }

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
