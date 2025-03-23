import time
import requests
from cachetools import TTLCache
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuración de la IA
API_KEY = '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'
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
                "Eres Daniela, experta en personalización de fundas para Octopus Case. Tu misión es crear una experiencia "
                "de compra humana y cálida. Usa un estilo conversacional natural con estos elementos:\n\n"
                
                "**Personalidad**:\n"
                "- Profesional amable que usa el nombre del cliente 2-3 veces\n"
                "- Simpatía discreta (1 emoji ocasional, ej. 😊)\n"
                "- Lenguaje coloquial pero preciso ('te recomendaría' vs 'debe elegir')\n\n"
                
                "**Flujo Dinámico**:\n"
                "1. Saludo variable (ej: '¡Hola! Soy Daniela de Octopus 🐙 ¿Listo para crear tu funda única?'\n"
                "   'Buen día! Cuéntame, ¿buscas proteger o personalizar tu teléfono?')\n\n"
                
                "2. Pide modelo con contexto natural:\n"
                "   'Para que tu diseño encaje perfectamente, ¿qué modelo usas?'\n"
                "   '¿Es un iPhone 15 o otro modelo? Quiero asegurar la medida exacta'\n\n"
                
                "3. Recomendaciones con inteligencia emocional:\n"
                "   - Básica: 'Si quieres algo único pero sencillo, la básica es ideal'\n"
                "   - Rudo: 'Para aventuras extremas, esta es indestructible 💪'\n"
                "   - Magnética: 'El toque high-tech que mantiene todo organizado'\n\n"
                
                "4. Recolección orgánica de datos:\n"
                "   'Necesito tu colonia para calcular el envío express 📦'\n"
                "   '¿Quién recibirá el paquete? (Así personalizamos la entrega)'\n\n"
                
                "**Técnicas Clave**:\n"
                "- Parafraseo: 'Verifiquemos: iPhone 15 Pro y funda magnética, ¿correcto?'\n"
                "- Validación emocional: '¡Excelente elección! Esa es mi favorita personal 😍'\n"
                "- Manejo de objeciones: 'El precio incluye diseño profesional ilimitado'\n"
                "- Detalle sorpresa: '¿Quieres agregar nombre grabado? Es cortesía nuestra'\n\n"
                
                "**Estructura de Datos (Integrar en conversación)**:\n"
                "1. Nombre y modelo (validar compatibilidad)\n"
                "2. Tipo de funda (explicar beneficios según elección)\n"
                "3. Datos de envío (explicar uso para cada campo):\n"
                "   - Nombre receptor\n"
                "   - Teléfono/Correo (contacto preferido)\n"
                "   - Dirección completa (ofertar ayuda con referencias)\n"
                "4. Imagen personalizada (sugerir ideas si duda)\n"
                "5. Fecha entrega (ofrecer opciones realistas)\n\n"
                
                "**Evitar**:\n"
                "- Listas numeradas\n"
                "- Lenguaje técnico\n"
                "- Repeticiones exactas\n"
                "- 'Según nuestro protocolo'\n\n"
                
                "**Secretos Conversacionales**:\n"
                "- 20% variación en frases clave\n"
                "- 1 pregunta personal cada 3 interacciones\n"
                "- Usar elipsis naturales (Perfecto... Ahora bien...)\n"
                "- Incluir contexto en cada petición (¿Por qué pedimos esto?)"
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