import random
from strands import Agent, tool


@tool
def get_balance(user_id: str) -> str:
    """Get balance of a RufusBank user.
    :param user_id (str): RufusBank user ID.
    """
    saldo = random.randint(1000, 100000)
    return f"El saldo del usuario {user_id} es de: {saldo} COP..."


agent = Agent(tools=[get_balance])
print(agent("(user_id: santi123) Cuánta plata tengo en mi cuenta?"))
