import { Dropbox } from 'dropbox'
import { secureConfig } from './secure-config'

export interface DropboxFile {
    name: string
    path: string
    id: string
    size: number
    clientModified: string
    serverModified: string
    rev: string
}

export class DropboxClient {
    private dbx: Dropbox
    private isConfigured: boolean = false

    constructor() {
        const config = secureConfig.getDropboxConfig()

        // Si tenemos credenciales, inicializar
        if (config.refreshToken && config.appKey && config.appSecret) {
            this.dbx = new Dropbox({
                clientId: config.appKey,
                clientSecret: config.appSecret,
                refreshToken: config.refreshToken,
            })
            this.isConfigured = true
        } else {
            console.warn('⚠️ Dropbox Client: Credenciales incompletas')
            // Inicializar dummy para evitar crash inmediato, pero fallará al usar
            this.dbx = new Dropbox({ accessToken: 'dummy' })
        }
    }

    /**
     * Verifica si el cliente está listo para usar
     */
    isReady(): boolean {
        return this.isConfigured
    }

    /**
     * Lista archivos en una carpeta
     * @param path Ruta de la carpeta (ej: '/Documentos' o '' para raíz)
     */
    async listFiles(path: string = ''): Promise<DropboxFile[]> {
        this.ensureReady()
        try {
            const response = await this.dbx.filesListFolder({
                path: path === '/' ? '' : path, // Dropbox prefiere string vacío para raíz
                recursive: false,
                include_media_info: false,
                include_deleted: false,
                include_has_explicit_shared_members: false
            })

            return response.result.entries
                .filter(entry => entry['.tag'] === 'file')
                .map(entry => ({
                    name: entry.name,
                    path: entry.path_display || entry.path_lower || '',
                    id: entry.id,
                    size: (entry as any).size || 0,
                    clientModified: (entry as any).client_modified,
                    serverModified: (entry as any).server_modified,
                    rev: (entry as any).rev
                }))
        } catch (error) {
            console.error('❌ Error listando archivos de Dropbox:', error)
            throw this.normalizeError(error)
        }
    }

    /**
     * Obtiene el link temporal de descarga de un archivo
     * @param path Ruta del archivo
     */
    async getTemporaryLink(path: string): Promise<string> {
        this.ensureReady()
        try {
            const response = await this.dbx.filesGetTemporaryLink({ path })
            return response.result.link
        } catch (error) {
            console.error('❌ Error obteniendo link de Dropbox:', error)
            throw this.normalizeError(error)
        }
    }

    /**
     * Descarga el contenido de text de un archivo
     * @param path Ruta del archivo
     */
    async downloadTextFile(path: string): Promise<string> {
        this.ensureReady()
        try {
            const response = await this.dbx.filesDownload({ path })
            // result.fileBinary contiene el buffer si se usa node-fetch, o blob en navegador
            // En entorno Node con dropbox sdk v10+, fileBinary suele ser el contenido

            const fileBinary = (response.result as any).fileBinary

            if (Buffer.isBuffer(fileBinary)) {
                return fileBinary.toString('utf-8')
            } else {
                throw new Error('Formato de archivo no soportado o error en descarga')
            }
        } catch (error) {
            console.error('❌ Error descargando archivo de Dropbox:', error)
            throw this.normalizeError(error)
        }
    }

    /**
     * Busca archivos que coincidan con la query
     */
    async searchFiles(query: string): Promise<DropboxFile[]> {
        this.ensureReady()
        try {
            const response = await this.dbx.filesSearchV2({
                query: query,
                options: {
                    file_status: { '.tag': 'active' },
                    filename_only: true
                }
            })

            return response.result.matches
                .map(match => match.metadata)
                .filter(meta => meta['.tag'] === 'metadata' && (meta as any).metadata['.tag'] === 'file')
                .map((meta: any) => {
                    const entry = meta.metadata
                    return {
                        name: entry.name,
                        path: entry.path_display || '',
                        id: entry.id,
                        size: entry.size,
                        clientModified: entry.client_modified,
                        serverModified: entry.server_modified,
                        rev: entry.rev
                    }
                })
        } catch (error) {
            console.error('❌ Error buscando en Dropbox:', error)
            throw this.normalizeError(error)
        }
    }

    private ensureReady() {
        if (!this.isConfigured) {
            throw new Error('Dropbox no está configurado. Faltan credenciales (Refresh Token).')
        }
    }

    private normalizeError(error: any): Error {
        const msg = error?.error?.error_summary || error?.message || 'Error desconocido en Dropbox'
        return new Error(msg)
    }
}

// Singleton export
export const dropboxClient = new DropboxClient()
