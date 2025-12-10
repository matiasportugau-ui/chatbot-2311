const { Dropbox } = require('dropbox');
const readline = require('readline');

// Configuración
const APP_KEY = process.env.DROPBOX_APP_KEY || 'c8jkxxfe9r3x3p9';
const APP_SECRET = process.env.DROPBOX_APP_SECRET || 'qlo3fyzjjaww5lk';

if (!APP_KEY || !APP_SECRET) {
    console.error('Error: Faltan las credenciales APP_KEY o APP_SECRET');
    process.exit(1);
}

const dbx = new Dropbox({
    clientId: APP_KEY,
    clientSecret: APP_SECRET,
});

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
});

async function getTokens() {
    // 1. Generar URL de autorización
    const authUrl = await dbx.auth.getAuthenticationUrl(
        'http://localhost:3000', // Redirect URI simplificado para copy-paste
        null,
        'code',
        'offline', // Importante para obtener refresh_token
        null,
        'none',
        false
    );

    console.log('\n🔐 CONFIGURACIÓN DE DROPBOX');
    console.log('============================');
    console.log('\n1. Por favor visita esta URL en tu navegador:');
    console.log('\n   ' + authUrl);
    console.log('\n2. Autoriza la aplicación.');
    console.log('3. Serás redirigido a una página (posiblemente con error de conexión, no importa).');
    console.log('4. Busca el parámetro "code" en la URL de la barra de direcciones.');
    console.log('   Ejemplo: http://localhost:3000/?code=AQUI_ESTA_EL_CODIGO&...');

    rl.question('\n✍️  Pega el CÓDIGO aquí: ', async (code) => {
        try {
            // 4. Intercambiar código por tokens
            const response = await dbx.auth.getAccessTokenFromCode(
                'http://localhost:3000',
                code.trim()
            );

            const { access_token, refresh_token } = response.result;

            console.log('\n✅ ¡AUTENTICACIÓN EXITOSA!');
            console.log('==========================');
            console.log('\nGuarda estos valores en tu archivo .env.local o usa el comando:');
            console.log('\npython3 unified_credentials_manager.py set --key DROPBOX_REFRESH_TOKEN --value ' + refresh_token + ' --save-to all');

            console.log('\n(El access token expira, el refresh token es permanente)\n');

        } catch (error) {
            console.error('\n❌ Error obteniendo el token:', error.message || error);
            if (error.response) {
                console.error('Detalles del error:', JSON.stringify(error.response.body || error.response, null, 2));
            }
            if (error.error) {
                console.error('Error info:', JSON.stringify(error.error, null, 2));
            }
        } finally {
            rl.close();
        }
    });
}

getTokens();
