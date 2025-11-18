import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'BMC Dashboard - WhatsApp Quoting System',
  description: 'Automated conversational quoting system powered by AI and n8n workflows',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        {children}
      </body>
    </html>
  )
}
