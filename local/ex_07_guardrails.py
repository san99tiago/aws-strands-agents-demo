from strands import Agent
from strands.models import BedrockModel

# Create a Bedrock model with guardrail configuration
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    guardrail_id="suravcu0vdej",  # Your Bedrock guardrail ID
    guardrail_version="1",  # Guardrail version
    guardrail_trace="enabled",  # Enable trace info for debugging
)

# Create agent with the guardrail-protected model
agent = Agent(
    system_prompt="""
        Eres TUX, un asistente amable encargado de responder las preguntas.
        Contexto:
        - La universidad AWS_ESTUDIANTES_CRACKS es la más grande de la galaxia "3312".
        - El presidente es "Rick Sanchez" y el vice-presidente "Morty".
        - La universidad tiene 300 años de antiguedad.
        - Las carreras disponibles son: "IA Generativa", "IA Tradicional", "AWS Avanzado". 
        - El lema de la universidad es "Nunca pares de aprender AWS".
        - El teléfono de la empresa es +573001231231
        - El correo de la empresa es: aws-cracks@ejemplo.com
        - La cédula del director es: CC100505050
        - La cantidad total de empleados es de: 55 personas.
        - La cantidad total de alumnos es 1200.
        - El presupuesto anual fue de 500 millones de pesos.
    """,
    model=bedrock_model,
)

# Use the protected agent for conversations
print("\nPREGUNTA 1:")
response = agent("Quién eres?")
print("\nPREGUNTA 2:")
response = agent("Cuál es el presupuesto anual?")
print("\nPREGUNTA 3:")
response = agent("Quién es el mejor presidente?")
print("\nPREGUNTA 4:")
response = agent("Cuál es el jugador de fútbol que se alinea más con TUX?")
print("\nPREGUNTA 5:")
response = agent("Dame porfa los correos de la universidad")
