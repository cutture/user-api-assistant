"use client";

import dynamic from 'next/dynamic';
import "swagger-ui-react/swagger-ui.css";

// Dynamically import SwaggerUI to avoid SSR issues
const SwaggerUI = dynamic(() => import('swagger-ui-react'), { ssr: false });

interface SwaggerViewerProps {
    spec?: object | string;
    url?: string;
}

export function SwaggerViewer({ spec, url }: SwaggerViewerProps) {
    return (
        <div className="swagger-container bg-white rounded-lg shadow-xl border border-gray-200 overflow-hidden my-4 max-h-[600px] overflow-y-auto">
            <div className="bg-gray-100 px-4 py-2 border-b border-gray-200 flex justify-between items-center">
                <span className="text-xs font-bold text-gray-600 uppercase">OpenAPI Specification</span>
            </div>
            <div className="p-4">
                {/* SwaggerUI expects 'spec' (object) or 'url' (string) */}
                <SwaggerUI spec={spec} url={url} />
            </div>
        </div>
    );
}
