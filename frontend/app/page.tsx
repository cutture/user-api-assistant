"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FileUpload } from "@/components/file-upload";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

interface Message {
  role: "user" | "assistant";
  content: string;
  plan?: string;
  context?: string[];
}

import dynamic from "next/dynamic";
import { SwaggerViewer } from "@/components/swagger-viewer";

const MermaidDiagram = dynamic(() => import("@/components/mermaid-diagram"), { ssr: false });

// Helper to parse message content into text and code blocks
const renderMessageContent = (content: string) => {
  // Regex to capture code blocks: ```lang ... ```
  // We use a non-capturing group for the optional language parsing inside the split if possible, 
  // but split captures the delimiter. 
  // Simple robust split:
  const parts = content.split(/(```[\w-]*\n[\s\S]*?```)/g);

  return parts.map((part, index) => {
    if (part.startsWith("```")) {
      // Robust Match
      // 1. Language (optional word after first ```)
      // 2. Content (everything else until the last ```)
      const match = part.match(/```([\w-]*)?\n([\s\S]*?)```/);

      let language = match ? match[1] || "text" : "text";
      const code = match ? match[2] : part.slice(3, -3);

      // Language Aliases for SyntaxHighlighter
      const langMap: Record<string, string> = {
        "jsx": "javascript",
        "tsx": "typescript",
        "py": "python",
        "sh": "bash",
        "js": "javascript",
        "ts": "typescript",
        "csharp": "csharp",
        "cs": "csharp",
        "dotnet": "csharp"
      };

      const displayLang = language || "text"; // Display strict name
      const highlightLang = langMap[language.toLowerCase()] || language || "text";

      if (highlightLang === "mermaid") {
        return <MermaidDiagram key={index} chart={code} />;
      }

      return (
        <div key={index} className="rounded-md overflow-hidden my-2 border border-white/20 shadow-lg relative group">
          <div className="bg-slate-950 px-3 py-1.5 text-xs text-gray-400 flex justify-between items-center border-b border-white/10">
            <span className="font-mono font-semibold uppercase">{displayLang}</span>
            <button
              onClick={() => {
                navigator.clipboard.writeText(code);
                // Optional: Add toast here
              }}
              className="hover:text-white transition-colors flex items-center gap-1 opacity-100 md:opacity-0 group-hover:opacity-100"
            >
              📋 Copy
            </button>
          </div>
          <SyntaxHighlighter
            language={highlightLang}
            style={vscDarkPlus}
            customStyle={{ margin: 0, padding: '1rem', borderRadius: 0, fontSize: '0.85rem', lineHeight: '1.5' }}
            showLineNumbers={true}
            wrapLines={true}
            PreTag="div"
          >
            {code}
          </SyntaxHighlighter>
        </div>
      );
    }
    // Render text with line breaks
    return <span key={index} className="whitespace-pre-wrap leading-relaxed">{part}</span>;
  });
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Prepare history (excluding the current user message which is being sent as query)
      const history = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: input,
          history: history
        }),
      });

      const data = await response.json();

      if (data.error) {
        throw new Error(data.details || data.error);
      }

      const assistantMessage: Message = {
        role: "assistant",
        content: data.response || "No code generated.",
        plan: data.plan,
        context: data.context,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `❌ Error: ${error.message || "Unknown error"}` },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExportPostman = async (plan: string, code: string) => {
    try {
      const response = await fetch("/api/export/postman", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plan, code }),
      });

      if (!response.ok) throw new Error("Export failed");

      const data = await response.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "antigravity-collection.json";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      alert("Failed to export Postman collection");
    }
  };

  return (
    <main className="flex min-h-screen flex-col">
      <header className="border-b border-white/10 p-4 bg-black/20 backdrop-blur-sm sticky top-0 z-10">
        <h1 className="text-2xl font-bold text-white text-center">
          🚀 Enterprise API Assistant
        </h1>
        <p className="text-center text-gray-400 text-sm">
          Ask me about APIs. I'll find docs, plan, and generate code.
        </p>
      </header>

      <div className="flex-1 flex flex-col md:flex-row gap-4 p-4 max-w-7xl mx-auto w-full">
        {/* Left Sidebar: Uploads & Stats */}
        <div className="w-full md:w-64 flex flex-col gap-4">
          <FileUpload />

          <Card className="bg-black/40 border-white/10 backdrop-blur flex-1 hidden md:flex">
            <CardHeader>
              <CardTitle className="text-white text-sm">📚 Knowledge Base</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-gray-400">
                Upload PDF, Word, JSON, or Text files here. I'll include them in my context!
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Chat Area */}
        <Card className="flex-1 flex flex-col bg-black/40 border-white/10 backdrop-blur">

          <CardHeader>
            <CardTitle className="text-white">💬 Chat</CardTitle>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col">
            <ScrollArea className="flex-1 pr-4 h-[60vh]">
              <div className="space-y-4">
                {messages.map((msg, i) => (
                  <div
                    key={i}
                    className={`p-3 rounded-lg ${msg.role === "user"
                      ? "bg-purple-600/50 ml-8"
                      : "bg-white/10 mr-8"
                      }`}
                  >
                    <p className="text-sm text-gray-300 mb-1">
                      {msg.role === "user" ? "You" : "🤖 Assistant"}
                    </p>
                    {msg.plan && (
                      <details className="mb-2">
                        <summary className="text-purple-300 cursor-pointer text-sm">
                          📋 View Plan
                        </summary>
                        <pre className="text-xs text-gray-400 mt-2 whitespace-pre-wrap">
                          {msg.plan}
                        </pre>
                      </details>
                    )}

                    <div className="text-white text-sm">
                      {renderMessageContent(msg.content)}
                    </div>

                    {msg.context && msg.context.length > 0 && (
                      <details className="mt-2">
                        <summary className="text-gray-400 cursor-pointer text-xs">
                          📚 Sources ({msg.context.length})
                        </summary>
                        <ul className="text-xs text-gray-500 mt-1 list-disc pl-4">
                          {msg.context.slice(0, 3).map((c, j) => (
                            <li key={j}>{c.substring(0, 100)}...</li>
                          ))}
                        </ul>
                      </details>
                    )}

                    {/* Action Buttons for Assistant */}
                    {msg.role === "assistant" && (
                      <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-white/10">
                        {/* Postman Export */}
                        {(msg.plan || msg.content.includes("```")) && (
                          <Button
                            variant="outline"
                            size="sm"
                            className="text-xs h-7 bg-transparent border-orange-500/50 text-orange-400 hover:bg-orange-500/10"
                            onClick={() => handleExportPostman(msg.plan || "", msg.content)}
                          >
                            🚀 Export to Postman
                          </Button>
                        )}

                        {/* Detect OpenAPI JSON in content */}
                        {msg.content.includes("openapi") && msg.content.includes("{") && (
                          <div className="w-full mt-2">
                            {/* Attempt to parse JSON block for Swagger */}
                            {(() => {
                              const match = msg.content.match(/```json\n([\s\S]*?)```/);
                              if (match) {
                                try {
                                  const spec = JSON.parse(match[1]);
                                  if (spec.openapi || spec.swagger) {
                                    return <SwaggerViewer spec={spec} />;
                                  }
                                } catch (e) { }
                              }
                              return null;
                            })()}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
                {isLoading && (
                  <div className="text-gray-400 animate-pulse p-3">
                    ⏳ Thinking...
                  </div>
                )}
                <div ref={scrollRef} />
              </div>
            </ScrollArea>

            <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
              <Textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="How do I integrate the Stripe API?"
                className="flex-1 bg-white/5 border-white/20 text-white resize-none"
                rows={2}
              />
              <Button
                type="submit"
                disabled={isLoading}
                className="bg-purple-600 hover:bg-purple-700"
              >
                {isLoading ? "..." : "Send"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
