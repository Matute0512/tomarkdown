import type { Metadata } from "next";
import { Inter} from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "./providers";


const inter = Inter({ subsets: ["latin"] });


export const metadata: Metadata = {
  title: "ToMarkdown.com.ar | PDF y Word a Markdown",
  description: "Utilidad ultra-rápida para convertir archivos a Markdown en memoria.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {

  return (
    // Agregamos suppressHydrationWarning para que Next.js no se queje por los cambios de clases en el <html>
    <html lang="es" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );

}
