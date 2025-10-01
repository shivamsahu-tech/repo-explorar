import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';

export default function MarkdownLoader({content}) {

  return (
    
    <ReactMarkdown
    remarkPlugins={[remarkGfm]}
    components={{
        code({node, inline, className, children, ...props}) {
        const match = /language-(\w+)/.exec(className || '');
        return !inline && match ? (
            <SyntaxHighlighter
            style={tomorrow}
            language={match[1]}
            PreTag="div"
            {...props}
            >
            {String(children).replace(/\n$/, '')}
            </SyntaxHighlighter>
        ) : (
            <code className="bg-gray-700 px-1.5 py-0.5 rounded text-sm" {...props}>
            {children}
            </code>
        );
        },
        a({node, children, ...props}) {
        return (
            <a 
            className="text-blue-400 hover:text-blue-300 underline" 
            target="_blank" 
            rel="noopener noreferrer"
            {...props}
            >
            {children}
            </a>
        );
        },
        ul({node, children, ...props}) {
        return <ul className="list-disc list-inside space-y-1" {...props}>{children}</ul>;
        },
        li({node, children, ...props}) {
        return <li className="text-gray-200" {...props}>{children}</li>;
        }
    }}
    >
    {content}
    </ReactMarkdown>

  );
}