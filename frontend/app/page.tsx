/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars */
"use client";

import { useState, useCallback, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, FileText, Copy, Check, Loader2, Moon, Sun, X, RefreshCcw } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Toaster, toast } from "sonner";
import { useTheme } from "next-themes";
import { convertDocumentToMarkdown } from "../services/api";

// Utilidad para formatear el peso del archivo a KB/MB
function formatBytes(bytes: number, decimals = 2) {
  if (!+bytes) return "0 Bytes";
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

export default function ToMarkdownApp() {
  const [file, setFile] = useState<File | null>(null);
  const [markdown, setMarkdown] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);

  const [mounted, setMounted] = useState(false);
  const { theme, setTheme, resolvedTheme } = useTheme();

  // Aseguramos que el componente solo se renderice en el cliente para evitar el FOUC
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setMounted(true);
  }, []);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setMarkdown("");
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
    onDropRejected: () => {
      toast.error("Archivo no soportado o excede los 10MB.");
    }
  });

  const handleConvert = async () => {
    if (!file) return;
    setIsLoading(true);
    try {
      const result = await convertDocumentToMarkdown(file);
      setMarkdown(result);
      toast.success("¡Documento convertido con éxito!");
    } catch (err) {
      // Casteamos el error explícitamente para TypeScript
      const error = err as Error;
      toast.error(error.message || "Error desconocido al procesar el archivo");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = async () => {
    if (!markdown) return;

    // 1. Intento con la API moderna
    if (navigator?.clipboard?.writeText) {
      try {
        await navigator.clipboard.writeText(markdown);
        setCopied(true);
        toast.success("¡Copiado al portapapeles!");
        setTimeout(() => setCopied(false), 2000);
        return;
      } catch {
        console.error("Falló la API moderna del portapapeles.");
      }
    }

    // 2. Fallback clásico (sin variables de error para evitar advertencias de unused-vars)
    try {
      const textArea = document.createElement("textarea");
      textArea.value = markdown;

      textArea.style.top = "0";
      textArea.style.left = "0";
      textArea.style.position = "fixed";
      textArea.style.opacity = "0";

      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();

      const successful = document.execCommand('copy');
      document.body.removeChild(textArea);

      if (successful) {
        setCopied(true);
        toast.success("¡Copiado al portapapeles! (Modo LAN)");
        setTimeout(() => setCopied(false), 2000);
      } else {
        toast.error("Tu navegador bloqueó el acceso al portapapeles.");
      }
    } catch {
      toast.error("Error inesperado al intentar copiar el texto.");
    }
  };

  const handleReset = (e: React.MouseEvent) => {
    e.stopPropagation();
    setFile(null);
    setMarkdown("");
  };

  return (
    <main className="min-h-screen bg-neutral-50 dark:bg-neutral-950 text-neutral-900 dark:text-neutral-100 font-sans p-6 md:p-12 transition-colors duration-300">

      {/* Forzamos el tipado correcto de Next Themes para el Toaster */}
      <Toaster position="bottom-right" richColors theme={theme as "light" | "dark" | "system"} />

      <div className="absolute top-6 right-6 md:top-12 md:right-12 min-h-[38px] min-w-[38px]">
        {mounted && (
          <button
            onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
            className="p-2 rounded-full bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-all shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Alternar tema"
          >
            {resolvedTheme === "dark" ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
        )}
      </div>

      <div className="max-w-4xl mx-auto space-y-8 mt-12 md:mt-4">

        <header className="text-center space-y-2">
          <h1 className="text-4xl font-extrabold tracking-tight text-neutral-900 dark:text-white">
            ToMarkdown<span className="text-blue-600 dark:text-blue-500">.com.ar</span>
          </h1>
          <p className="text-neutral-500 dark:text-neutral-400 text-lg">
            Convierte tus archivos PDF y Word a Markdown al instante.
          </p>
        </header>

        <section
          {...getRootProps()}
          className={`relative border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center text-center cursor-pointer transition-colors
            ${isDragActive ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20" : "border-neutral-300 dark:border-neutral-700 hover:bg-neutral-100 dark:hover:bg-neutral-800 bg-white dark:bg-neutral-900"}
            ${isDragReject ? "border-red-500 bg-red-50 dark:bg-red-900/20" : ""}
          `}
        >
          <input {...getInputProps()} />
          <UploadCloud className={`w-12 h-12 mb-4 transition-transform ${isDragActive ? "text-blue-500 scale-110" : "text-neutral-400 dark:text-neutral-500"}`} />

          {file ? (
            <div className="flex items-center space-x-4 bg-green-50 dark:bg-green-900/10 px-4 py-3 rounded-lg border border-green-200 dark:border-green-800 shadow-sm animate-in zoom-in-95 duration-200">
              <FileText className="w-6 h-6 text-green-700 dark:text-green-500 flex-shrink-0" />
              <div className="flex flex-col text-left overflow-hidden">
                <span className="text-sm font-semibold text-green-800 dark:text-green-300 truncate max-w-[200px] md:max-w-xs">{file.name}</span>
                <span className="text-xs text-green-600 dark:text-green-500/80">{formatBytes(file.size)}</span>
              </div>
              <button
                onClick={handleReset}
                className="ml-2 p-1.5 hover:bg-green-200 dark:hover:bg-green-800/50 rounded-full transition-colors focus:outline-none"
                title="Quitar archivo"
              >
                <X className="w-4 h-4 text-green-700 dark:text-green-400" />
              </button>
            </div>
          ) : (
            <p className="text-neutral-600 dark:text-neutral-300 font-medium">
              Arrastra y suelta tu archivo aquí, o haz clic para seleccionar
            </p>
          )}
          <p className="text-sm text-neutral-400 dark:text-neutral-500 mt-3">Soporta .pdf y .docx (Max 10MB)</p>
        </section>

        <div className="flex justify-center">
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleConvert();
            }}
            disabled={!file || isLoading}
            className="flex items-center justify-center px-8 py-3 text-white dark:text-neutral-900 bg-neutral-900 dark:bg-white rounded-lg font-semibold hover:bg-neutral-800 dark:hover:bg-neutral-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-95"
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

        {markdown && (
          <section className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl overflow-hidden shadow-sm animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-center px-4 py-3 bg-neutral-100 dark:bg-neutral-800/50 border-b border-neutral-200 dark:border-neutral-800">
              <span className="text-sm font-semibold text-neutral-600 dark:text-neutral-400 flex items-center">
                Resultado Markdown
              </span>
              <div className="flex space-x-2">
                <button
                  onClick={handleReset}
                  className="flex items-center px-2 py-1 text-sm font-medium text-neutral-500 dark:text-neutral-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                  title="Limpiar resultado"
                >
                  <RefreshCcw className="w-4 h-4" />
                </button>
                <button
                  onClick={handleCopy}
                  className="flex items-center px-3 py-1 text-sm font-medium text-neutral-700 dark:text-neutral-200 bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-md hover:bg-neutral-50 dark:hover:bg-neutral-700 transition-colors"
                >
                  {copied ? (
                    <><Check className="w-4 h-4 mr-1.5 text-green-600 dark:text-green-400" /> Copiado</>
                  ) : (
                    <><Copy className="w-4 h-4 mr-1.5" /> Copiar</>
                  )}
                </button>
              </div>
            </div>

            <div className="p-6 overflow-auto max-h-[600px] bg-[#1E1E1E]">
              {/* Silenciamos los tipos específicos de react-markdown que causan conflicto */}
              {/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars */}
              <ReactMarkdown
                components={{
                  code({ node, inline, className, children, ...props }: any) {
                    const match = /language-(\w+)/.exec(className || "");
                    return !inline && match ? (
                      <SyntaxHighlighter
                        style={vscDarkPlus as any}
                        language={match[1]}
                        PreTag="div"
                        {...props}
                      >
                        {String(children).replace(/\n$/, "")}
                      </SyntaxHighlighter>
                    ) : (
                      <code className="bg-neutral-800 text-blue-300 px-1.5 py-0.5 rounded-md text-sm" {...props}>
                        {children}
                      </code>
                    );
                  },
                  h1: ({node, ...props}) => <h1 className="text-3xl font-bold text-white mb-4 mt-6 border-b border-neutral-700 pb-2" {...props} />,
                  h2: ({node, ...props}) => <h2 className="text-2xl font-semibold text-white mb-3 mt-5 border-b border-neutral-700 pb-1" {...props} />,
                  h3: ({node, ...props}) => <h3 className="text-xl font-medium text-white mb-3 mt-4" {...props} />,
                  p: ({node, ...props}) => <p className="text-neutral-300 mb-4 leading-relaxed" {...props} />,
                  ul: ({node, ...props}) => <ul className="list-disc list-inside text-neutral-300 mb-4" {...props} />,
                  ol: ({node, ...props}) => <ol className="list-decimal list-inside text-neutral-300 mb-4" {...props} />,
                }}
              >
                {markdown}
              </ReactMarkdown>
              {/* eslint-enable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars */}
            </div>
          </section>
        )}

      </div>
    </main>
  );
}