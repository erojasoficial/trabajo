from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = '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'
socketio = SocketIO(app, cors_allowed_origins='*')
CORS(app)

chat_history = ""
PROMPT_ORIGINAL = "Actúa como un Asistente virtual de ventas y gestión de pagos de servicios. Realiza la siguiente tarea: ayudar a los usuarios a pagar sus servicios y proporcionar sus deudas personalizados con empatía y simplicidad. con no mas de 2 preguntas . La información complementaria es la siguiente: Como Asistente Virtual de Ventas y Gestión de Pagos de Servicios, ChatGPT se encargará de realizar el pago de servicios y brindar deudas personalizadas para cada usuario. El sistema se centrará en ser empático y simplificar la experiencia, solicitando solo la información mínima necesaria para ofrecer un precio adecuado y ajustado a las necesidades del cliente. En caso el usuario requiera saber su deuda no responder con una negativa y generarle su deuda para que tu la pagues. La respuesta está dirigida a: en cualquier persona interesada en tener un Asistente Virtual de Ventas y Gestión de Pagos de Servicios, ya sea para simplificar sus pagos mensuales de servicios o para recibir precios personalizados y ajustados a sus necesidades."

def get_gpt_response(message):
    global chat_history

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + "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"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "assistant", "content": PROMPT_ORIGINAL + chat_history + message}]
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=json.dumps(data))
    response_json = response.json()

    chat_history += "esta es una solicitud del cliente y tienes que responderla si la solicitud no es continua obviarla:"+message + "\n"
    
    if response_json.get('choices'):
        return response_json['choices'][0]['message']['content']
    else:
        return "No se pudo obtener una respuesta del modelo GPT."

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(data):
    global chat_history

    message = data['message']
    gpt_response = get_gpt_response(message)

    response = {
        "respuesta": gpt_response.replace("\n\n", " ")
    }
    
    emit('response', response)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8082)
