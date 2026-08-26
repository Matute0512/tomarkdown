"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, FileText, FileWarning, Copy, Check, Loader2 } from "lucide-react";
import { convertDocumentToMarkdown } from "../services/api";

export default function ToMarkdownApp() {
  const [file, setFile] = useState<File | null>(null);
  const [markdown, setMarkdown] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);

  // Configuración de react-dropzone
  const onDrop = useCallback((acceptedFiles: File[]) => {
    setError(null);
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setMarkdown(""); // Limpiar resultado anterior
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10 MB (Debe coincidir con nuestro backend)
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
  });

  const handleConvert = async () => {
    if (!file) return;

    setIsLoading(true);
    setError(null);

    try {
      const result = await convertDocumentToMarkdown(file);
      setMarkdown(result);
    } catch (err: any) {
      setError(err.message || "Error desconocido");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = () => {
    if (!markdown) return;
    navigator.clipboard.writeText(markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <main className="min-h-screen bg-neutral-50 text-neutral-900 font-sans p-6 md:p-12">
      <div className="max-w-4xl mx-auto space-y-8">

        {/* Cabecera */}
        <header className="text-center space-y-2">
          <h1 className="text-4xl font-extrabold tracking-tight text-neutral-900">
            ToMarkdown<span className="text-blue-600">.com</span>
          </h1>
          <p className="text-neutral-500 text-lg">
            Convierte tus archivos PDF y Word a Markdown al instante.
          </p>
        </header>

        {/* Zona de Dropzone */}
        <section
          {...getRootProps()}
          className={`relative border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center text-center cursor-pointer transition-colors
            ${isDragActive ? "border-blue-500 bg-blue-50" : "border-neutral-300 hover:bg-neutral-100 bg-white"}
            ${isDragReject ? "border-red-500 bg-red-50" : ""}
          `}
        >
          <input {...getInputProps()} />
          <UploadCloud className={`w-12 h-12 mb-4 ${isDragActive ? "text-blue-500" : "text-neutral-400"}`} />

          {file ? (
            <div className="flex items-center space-x-2 text-green-700 font-medium">
              <FileText className="w-5 h-5" />
              <span>{file.name}</span>
            </div>
          ) : (
            <p className="text-neutral-600 font-medium">
              Arrastra y suelta tu archivo aquí, o haz clic para seleccionar
            </p>
          )}
          <p className="text-sm text-neutral-400 mt-2">Soporta .pdf y .docx (Max 10MB)</p>
        </section>

        {/* Errores visuales */}
        {error && (
          <div className="flex items-center p-4 text-red-800 bg-red-100 rounded-lg">
            <FileWarning className="w-5 h-5 mr-2 flex-shrink-0" />
            <p>{error}</p>
          </div>
        )}

        {/* Botón de Acción */}
        <div className="flex justify-center">
          <button
            onClick={(e) => {
              e.stopPropagation(); // Evitar que el click se propague al dropzone
              handleConvert();
            }}
            disabled={!file || isLoading}
            className="flex items-center justify-center px-8 py-3 text-white bg-neutral-900 rounded-lg font-semibold hover:bg-neutral-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Procesando...
              </>
            ) : (
              "Convertir a Markdown"
            )}
          </button>
        </div>

        {/* Vista previa del Resultado */}
        {markdown && (
          <section className="bg-white border border-neutral-200 rounded-xl overflow-hidden shadow-sm animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-center px-4 py-3 bg-neutral-100 border-b border-neutral-200">
              <span className="text-sm font-semibold text-neutral-600">Resultado Markdown</span>
              <button
                onClick={handleCopy}
                className="flex items-center text-sm font-medium text-neutral-700 hover:text-blue-600 transition-colors"
              >
                {copied ? (
                  <><Check className="w-4 h-4 mr-1 text-green-600" /> ¡Copiado!</>
                ) : (
                  <><Copy className="w-4 h-4 mr-1" /> Copiar al portapapeles</>
                )}
              </button>
            </div>
            <div className="p-4 overflow-auto max-h-[500px]">
              <pre className="text-sm text-neutral-800 whitespace-pre-wrap font-mono">
                {markdown}
              </pre>
            </div>
          </section>
        )}

      </div>
    </main>
  );
}
