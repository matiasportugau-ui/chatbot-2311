
const { Dropbox } = require('dropbox');

// Cargar variables si no están (para prueba aislada)
const accessToken = process.env.DROPBOX_ACCESS_TOKEN;
const refreshToken = process.env.DROPBOX_REFRESH_TOKEN;
const appKey = process.env.DROPBOX_APP_KEY;
const appSecret = process.env.DROPBOX_APP_SECRET;

async function verify() {
    console.log('🔍 Verificando conexión a Dropbox...');

    if (!refreshToken || !appKey || !appSecret) {
        console.error('❌ Falta configuración (Refresh Token, App Key o Secret)');
        try {
            // Intentar leer de unified_credentials si falla env normal
            console.log('Intentando leer de unified_credentials_manager...');
            const secrets = require('../unified_credentials_manager.py'); // Esto no funcionaría directamente en JS node puro sin spawn
            // En su lugar, asumimos que el usuario ya cargó las vars o usamos el comando python para verificarlas
        } catch (e) { }
        // Seguir solo si hay algo
    }

    // Usar refresh token para obtener nuevo access token
    const dbx = new Dropbox({
        clientId: appKey,
        clientSecret: appSecret,
        refreshToken: refreshToken
    });

    try {
        const response = await dbx.filesListFolder({ path: '' });
        console.log('\n✅ ¡Conexión Exitosa!');
        console.log(`📂 Archivos en raíz: ${response.result.entries.length}`);
        response.result.entries.slice(0, 5).forEach(f => {
            console.log(`   - ${f['.tag'] === 'folder' ? '📁' : '📄'} ${f.name}`);
        });
    } catch (error) {
        console.error('❌ Error de conexión:', error);
    }
}

verify();
