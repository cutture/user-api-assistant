"use client";

import { useEffect, useRef } from "react";
import mermaid from "mermaid";

mermaid.initialize({
    startOnLoad: false,
    theme: "dark",
    securityLevel: "loose",
});

interface MermaidProps {
    chart: string;
}

export default function MermaidDiagram({ chart }: MermaidProps) {
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (ref.current) {
            mermaid.contentLoaded();
            const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
            ref.current.innerHTML = "";

            try {
                mermaid.render(id, chart).then(({ svg }) => {
                    if (ref.current) {
                        ref.current.innerHTML = svg;
                    }
                });
            } catch (error) {
                console.error("Mermaid render error:", error);
                ref.current.innerText = "Error rendering diagram.";
            }
        }
    }, [chart]);

    return <div ref={ref} className="overflow-x-auto p-4 bg-white/5 rounded-lg" />;
}
