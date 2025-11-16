import traceback
from partidas import dialogflow_client

print('Probando Dialogflow client...')
try:
    resp = dialogflow_client.get_chat_response('Hola, ¿puedes saludarme en pocas palabras?')
    print('== RESPONSE ==')
    print(resp)
except Exception as e:
    print('== EXCEPTION ==')
    traceback.print_exc()
