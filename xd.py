import time
import requests
from cachetools import TTLCache
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuración de la IA
API_KEY = ''
MODEL = 'deepseek/deepseek-r1:free'
URL = 'https://openrouter.ai/api/v1/chat/completions'

# Memoria de conversaciones (5 minutos)
cache = TTLCache(maxsize=100, ttl=300)

def get_ai_response(user_number, message):
    # Recuperar o crear historial
    history = cache.get(user_number, [
        {
            "role": "system",
            "content": (
                "Eres Daniela, la asistente virtual de Octopus Case. Eres una experta en fundas personalizadas para teléfonos y te destacas por "
                "ser amigable, profesional y con un toque sutil de simpatía. Ayudas a los clientes a elegir y comprar fundas de teléfono de la siguiente manera:\n"
                "1. Saluda y preséntate como Daniela.\n"
                "2. Pregunta el nombre del cliente y el modelo de su teléfono.\n"
                "3. Una vez recibido el modelo, ofrece tres opciones de fundas personalizadas:\n"
                "   - Funda básica ($350): Diseño personalizado con la imagen que prefieras.\n"
                "   - Funda uso rudo ($400): Mayor protección y durabilidad con recubrimiento epóxico.\n"
                "   - Funda magnética ($500): Ideal para superficies metálicas.\n"
                "4. Si el cliente elige una opción, solicita los siguientes datos para completar el pedido:\n"
                "   - Nombre de quien recibe\n"
                "   - Teléfono\n"
                "   - Correo\n"
                "   - Calle y número\n"
                "   - Colonia\n"
                "   - Ciudad\n"
                "   - Estado\n"
                "   - Referencia\n"
                "5. Pregunta si ya tiene la imagen que desea utilizar y, de ser afirmativo, indícale que realice un anticipo y envíe el comprobante.\n"
                "6. Pregunta la fecha de entrega deseada y confirma que un ejecutivo dará seguimiento a su pedido.\n"
                "7. Si el cliente tiene dudas sobre el proceso de pago, ofrécele asistencia de manera clara y cordial.\n"
                "Mantén un tono amistoso, cercano y profesional."
            )
        }
    ])
    
    # Agregar nuevo mensaje al historial
    history.append({"role": "user", "content": message})
    
    # Construir payload
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'HTTP-Referer': 'https://openrouter.ai/',
        'X-Title': 'OctopusCase',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "model": MODEL,
        "messages": history,
        "max_tokens": 500
    }
    
    while True:
        try:
            response = requests.post(URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            if data.get('choices'):
                ai_response = data['choices'][0]['message']['content']
                if len(ai_response.split()) >= 2:  # Verificar que la respuesta tenga al menos 2 palabras
                    # Actualizar historial
                    history.append({"role": "assistant", "content": ai_response})
                    cache[user_number] = history
                    return ai_response
            else:
                print("❌ Ocurrió un error al procesar tu solicitud.")
                
        except Exception as e:
            print(f"Error en la API: {str(e)}")
        
        time.sleep(1)  # Esperar 1 segundo antes de intentar nuevamente

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    user_number = data.get('number')
    message = data.get('message')
    
    if not user_number or not message:
        return jsonify({"error": "Datos incompletos"}), 400
    
    response = get_ai_response(user_number, message)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)