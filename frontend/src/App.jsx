import { useState } from 'react'
import { FileText } from 'lucide-react'
import { ThemeToggle } from './components/ThemeToggle'
import { DocumentUpload } from './components/DocumentUpload'
import { ChatInterface } from './components/ChatInterface'

function App() {
  const [currentDocumentId, setCurrentDocumentId] = useState(null)

  const handleDocumentReady = (documentId) => {
    setCurrentDocumentId(documentId)
  }

  const handleNewDocument = () => {
    setCurrentDocumentId(null)
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="border-b border-border">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5 sm:h-6 sm:w-6 text-primary" />
            <h1 className="text-lg sm:text-2xl font-bold">DocuChat AI</h1>
          </div>
          <div className="flex items-center gap-2">
            {currentDocumentId && (
              <button
                onClick={handleNewDocument}
                className="text-xs sm:text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                Upload New
              </button>
            )}
            <ThemeToggle />
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8 flex-1 flex items-center justify-center">
        <div className="w-full">
          {!currentDocumentId ? (
            <DocumentUpload onDocumentReady={handleDocumentReady} />
          ) : (
            <ChatInterface documentId={currentDocumentId} />
          )}
        </div>
      </main>

      <footer className="border-t border-border mt-auto">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 text-xs sm:text-sm text-muted-foreground">
            <p>Use AI-powered RAG to ask questions about document content</p>
            <div className="flex items-center gap-4">
              <span>v1.0</span>
              <a
                href="https://www.linkedin.com/in/natasha-dos-reis-98987431/"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-foreground transition-colors underline"
              >
                About the developer
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
