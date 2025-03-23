const venom = require('venom-bot');
const axios = require('axios');
const path = require('path');
const fs = require('fs');

const sessionFolder = path.join(__dirname, 'tokens');
const FLASK_ENDPOINT = 'http://127.0.0.1:3000/webhook';

// Crear carpeta tokens si no existe
if (!fs.existsSync(sessionFolder)) {
  fs.mkdirSync(sessionFolder);
}

venom
  .create({
    session: 'octopus-case-bot',
    folderNameToken: sessionFolder,
    headless: true,
    multidevice: true,
    logQR: true,
    catchQR: (base64Qr, asciiQR) => {
      console.log('Escanea este QR en WhatsApp Web:\n');
      console.log(asciiQR);
    },
    puppeteerOptions: { 
      args: ['--no-sandbox', '--disable-setuid-sandbox'] 
    }
  })
  .then((client) => {
    console.log('✅ Sesión iniciada correctamente');
    setupClient(client);
  })
  .catch((err) => {
    console.error('Error al iniciar:', err);
  });

function setupClient(client) {
  client.onStateChange(handleStateChange);
  
  // Manejador de mensajes
  client.onMessage(async (message) => {
    try {
      // Ignorar grupos y mensajes sin contenido
      if (message.isGroupMsg || !message.body) return;

      // Enviar mensaje a la API de Python
      const response = await axios.post(FLASK_ENDPOINT, {
        number: message.from,
        message: message.body
      });

      // Enviar respuesta al usuario
      await client.sendText(message.from, response.data.response);
      
    } catch (error) {
      console.error('Error:', error.response?.data || error.message);
      await client.sendText(message.from, '🔧 Ocurrió un error, intenta de nuevo más tarde.');
    }
  });
}

function handleStateChange(state) {
  const statusMessages = {
    CONFLICT: "Conflicto de sesión. Cierra WhatsApp Web en otros dispositivos.",
    CONNECTED: "Conectado",
    DISCONNECTED: "Desconectado",
    QRCODE_TIMEOUT: "QR expirado. Reinicia el bot.",
  };
  console.log(statusMessages[state] || `Estado: ${state}`);
}