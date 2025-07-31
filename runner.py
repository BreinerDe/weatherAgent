from google.adk.runners import Runner
from sessions import session_service_stateful, APP_NAME, USER_ID_STATEFUL, SESSION_ID_STATEFUL
from agents.root_agent import create_root_agent
from dotenv import load_dotenv

load_dotenv()

def create_runner():
    
    root_agent = create_root_agent()

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service_stateful,
    )
    print(f"✅ Runner created for guardrail agent '{runner.agent.name}', using stateful session service.")
    return runner

async def call_agent_async(query: str, runner, user_id, session_id):
    from google.genai import types
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
