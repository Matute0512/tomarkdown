/**
 * URL base de la API backend.
 * Configurable vía NEXT_PUBLIC_API_URL (se inyecta en el build de Next.js).
 * Por defecto apunta al backend local de desarrollo.
 */
const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/+$/, "");

/**
 * Excepción personalizada para manejar errores de la API en el frontend.
 */
export class ConversionError extends Error {
  constructor(public message: string, public statusCode?: number) {
    super(message);
    this.name = "ConversionError";
  }
}

/**
 * Envía el archivo al backend de FastAPI y devuelve el Markdown resultante.
 */
export async function convertDocumentToMarkdown(file: File): Promise<string> {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/convert`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ConversionError(
        errorData.detail || "Ocurrió un error inesperado al procesar el archivo.",
        response.status
      );
    }

    const data = await response.json();
    return data.markdown;

  } catch (error) {
    if (error instanceof ConversionError) {
      throw error;
    }
    throw new ConversionError("No se pudo conectar con el servidor. Verifica que el backend esté en ejecución.");
  }
}