import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import MessageRole, FilePurpose, FunctionTool, FileSearchTool, ToolSet
from dotenv import load_dotenv

load_dotenv(override=True)

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential()
)

agent = project_client.agents.create_agent(
    model="gpt-4o",
    name="my-agent",
    instructions= """
    You are a cheeky, pizza loving assistant for a brand called Pizza Lover. You help customers build their perfect pizza by guiding them through size, crust, toppings, and quantity.

You always ask for the customer's name before starting an order and remember it throughout the conversation.

You only respond to pizza-related questions. If asked about anything else, politely redirect the customer back to pizza topics."""
)
print(f"Created agent, ID: {agent.id}")

thread = project_client.agents.threads.create()
print(f"Created thread, ID: {thread.id}")

customer_name = None
pizza_keywords = ["pizza", "crust", "topping", "order", "sauce", "cheese", "pepperoni", "menu", "size", "slice"]

while True:

    # Get the user input
    user_input = input("You: ")

    # Break out of the loop
    if user_input.lower() in ["exit", "quit"]:
        break

    #Ask for name of the user
    if not customer_name:
        print("Pizza Lover: Before we get started, what is your name")
        customer_name = input("You: ")
        print(f"Pizza Lover: Great, {customer_name}! Let's build your perfect pizza")
        continue

    if not any(keyword in user_input.lower() for keyword in pizza_keywords):
        print("Pizza Lover: I'm all about pizza! Ask me anything crusty, cheesy, or saucy")
        continue

    enriched_input = f"My name is {customer_name}. {user_input}"

    # Add a message to the thread
    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER, 
        content=user_input
    )

    run = project_client.agents.runs.create_and_process(  
        thread_id=thread.id, 
        agent_id=agent.id
    );

    messages = project_client.agents.messages.list(thread_id=thread.id)  
    first_message = next(iter(messages), None) 
    if first_message: 
        print(next((item["text"]["value"] for item in first_message.content if item.get("type") == "text"), ""));

project_client.agents.delete_agent(agent.id)
print("Deleted agent");