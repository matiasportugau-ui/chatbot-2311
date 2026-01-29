import axios from 'axios';

export async function getWhatsAppMediaUrl(mediaId: string): Promise<string> {
  const accessToken = process.env.WHATSAPP_ACCESS_TOKEN;
  if (!accessToken) {
    throw new Error('WHATSAPP_ACCESS_TOKEN not configured');
  }
  
  const response = await axios.get(`https://graph.facebook.com/v18.0/${mediaId}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
  
  if (!response.data || !response.data.url) {
    throw new Error('Failed to get media URL from WhatsApp API');
  }
  
  return response.data.url;
}

export async function downloadWhatsAppMedia(url: string): Promise<Buffer> {
  const accessToken = process.env.WHATSAPP_ACCESS_TOKEN;
  if (!accessToken) {
    throw new Error('WHATSAPP_ACCESS_TOKEN not configured');
  }

  const response = await axios.get(url, {
    responseType: 'arraybuffer',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
  
  return Buffer.from(response.data);
}
