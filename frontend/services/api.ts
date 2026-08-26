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
    const response = await fetch("http://localhost:8000/api/v1/convert", {
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