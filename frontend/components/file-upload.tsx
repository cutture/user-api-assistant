"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function FileUpload() {
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [message, setMessage] = useState("");

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            setMessage("");
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setMessage("");

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch("/api/upload", {
                method: "POST",
                body: formData,
            });

            const data = await res.json();

            if (res.ok) {
                setMessage(`✅ Uploaded! Added ${data.chunks_added} chunks.`);
                setFile(null);
            } else {
                setMessage(`❌ Error: ${data.details || "Upload failed"}`);
            }
        } catch (error) {
            setMessage("❌ Connection error");
        } finally {
            setUploading(false);
        }
    };

    return (
        <Card className="bg-black/40 border-white/10 backdrop-blur w-full">
            <CardHeader className="pb-2">
                <CardTitle className="text-white text-sm">📄 Upload Context</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
                <Input
                    type="file"
                    accept=".pdf,.docx,.txt,.md,.json,.csv"
                    onChange={handleFileChange}
                    className="text-gray-300 bg-white/5 border-white/20 file:text-white file:bg-purple-600 file:border-0 file:rounded-md file:px-2 file:py-1 file:mr-2 file:text-xs"
                />
                <Button
                    onClick={handleUpload}
                    disabled={!file || uploading}
                    size="sm"
                    className="w-full bg-purple-600 hover:bg-purple-700 text-white"
                >
                    {uploading ? "Uploading..." : "Upload & Embed"}
                </Button>
                {message && (
                    <p className="text-xs text-center mt-2 text-gray-300 animate-pulse">
                        {message}
                    </p>
                )}
            </CardContent>
        </Card>
    );
}
