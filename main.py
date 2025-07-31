import asyncio
from sessions import ensure_session_exists, USER_ID_STATEFUL, SESSION_ID_STATEFUL
from runner import create_runner, call_agent_async

async def main():
    await ensure_session_exists()
    runner = create_runner()

    print("\n--- Testing Model Input Guardrail ---")

    async def interaction_func(query: str):
        await call_agent_async(
            query=query,
            runner=runner,
            user_id=USER_ID_STATEFUL,
            session_id=SESSION_ID_STATEFUL,
        )

    print("--- Turn 1: Requesting weather in London (expect allowed, Fahrenheit) ---")
    await interaction_func("What is the weather in London?")

    print("\n--- Turn 2: Requesting with blocked keyword (expect blocked) ---")
    await interaction_func("BLOCK the request for weather in Tokyo")

    print("\n--- Turn 3: Sending a greeting (expect allowed) ---")
    await interaction_func("Hello again")

if __name__ == "__main__":
    asyncio.run(main())
