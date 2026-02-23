import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
    children?: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null,
        errorInfo: null
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error, errorInfo: null };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Uncaught error:', error, errorInfo);
        this.setState({ error, errorInfo });
    }

    public render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <div className="p-8 max-w-4xl mx-auto mt-10">
                    <div className="bg-red-50 border border-red-200 rounded-lg p-6 shadow-lg">
                        <h1 className="text-2xl font-bold text-red-700 mb-4">Something went wrong</h1>
                        <p className="text-red-600 mb-4">
                            {this.state.error?.toString()}
                        </p>
                        {this.state.errorInfo && (
                            <details className="mt-4">
                                <summary className="text-sm font-medium text-red-500 cursor-pointer">Stack Trace</summary>
                                <pre className="mt-2 p-4 bg-red-100 rounded text-xs text-red-800 overflow-auto whitespace-pre-wrap font-mono">
                                    {this.state.errorInfo.componentStack}
                                </pre>
                            </details>
                        )}
                        <button
                            onClick={() => window.location.reload()}
                            className="mt-6 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                        >
                            Reload Application
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
