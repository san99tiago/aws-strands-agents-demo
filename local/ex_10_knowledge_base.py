import os
from strands import Agent
from strands_tools import memory, use_agent

# Set knowledge base ID (can be overridden by environment variable)
KB_ID = os.environ.get("KB_ID", "YWPHVL3IHM")
os.environ["STRANDS_KNOWLEDGE_BASE_ID"] = KB_ID


def run_kb_agent(query):
    """Process a user query with the knowledge base agent."""
    agent = Agent(tools=[memory, use_agent])

    # For retrieve actions, query the knowledge base with appropriate parameters
    result = agent.tool.use_agent(action="retrieve", query=query)
    # Convert the result to a string to extract just the content text
    result_str = str(result)
    print(result_str)

    # Generate a clear, conversational answer using the retrieved information
    answer = agent.tool.use_agent(
        prompt=f'User question: "{query}"\n\nInformation from knowledge base:\n{result_str}\n\nStart your answer with newline character and provide a helpful answer based on this information:',
        system_prompt="You are RUFFY, a friendly agent specialized in helping customers with their inquiries. Be friendly and always answer politely.",
    )


if __name__ == "__main__":
    # Print welcome message
    print("\n🧠 RUFFY agent with knowledge base🧠\n")

    # Interactive loop
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() in ["exit", "quit"]:
                print("\nGoodbye! 👋")
                break

            if not user_input.strip():
                continue

            # Process the input through the knowledge base agent
            print("Processing...")
            run_kb_agent(user_input)

        except KeyboardInterrupt:
            print("\n\nExecution interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
