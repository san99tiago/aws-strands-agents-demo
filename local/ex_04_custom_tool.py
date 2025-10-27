import random
from strands import Agent, tool
import boto3
from strands.models import BedrockModel


client = boto3.client("dynamodb", region_name="us-east-1")
bedrock_model1 = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    params={"max_tokens": 1600, "temperature": 0.7},
)


@tool
def get_balance(user_id: str) -> str:
    """Get balance of a  user.
    :param user_id (str):  user ID.
    """
    saldo = random.randint(1000, 100000)
    return f"El saldo del usuario {user_id} es de: {saldo} COP..."


@tool
def get_user_profile(user_id: str) -> str:
    """Get user profile from DynamoDB.
    :param user_id (str): User ID to fetch profile for.
    """
    try:
        response = client.get_item(
            TableName="techsummit-agentcore-prod",  # Update as needed
            Key={"PK": {"S": f"USER#{user_id}"}, "SK": {"S": "PROFILE"}},
        )

        if "Item" in response:
            return f"Perfil encontrado para usuario {user_id}: {response['Item']}"
        else:
            return f"No se encontró perfil para el usuario {user_id}"
    except Exception as e:
        return f"Error consultando perfil: {str(e)}"


agent = Agent(model=bedrock_model1, tools=[get_balance, get_user_profile])
print(agent("(user_id: santigrc) Cuánta plata tengo en mi cuenta?"))
print(agent("(user_id: santigrc) Muéstrame mi perfil de usuario"))
