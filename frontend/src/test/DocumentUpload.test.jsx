import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { DocumentUpload } from '../components/DocumentUpload'

vi.mock('@/services/api', () => ({
  documentService: {
    upload: vi.fn(),
    getStatus: vi.fn(),
  },
}))

vi.mock('@/hooks/useDocumentStatus', () => ({
  useDocumentStatus: vi.fn(() => ({
    status: null,
    error: null,
    loading: false,
  })),
}))

describe('DocumentUpload', () => {
  const mockOnDocumentReady = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders upload area', () => {
    render(<DocumentUpload onDocumentReady={mockOnDocumentReady} />)
    expect(screen.getByText(/click to upload or drag and drop/i)).toBeInTheDocument()
  })

  it('displays file name after selection', async () => {
    render(<DocumentUpload onDocumentReady={mockOnDocumentReady} />)
    
    const file = new File(['content'], 'test.pdf', { type: 'application/pdf' })
    const input = screen.getByRole('button').querySelector('input')
    
    await userEvent.upload(input, file)
    
    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument()
    })
  })

  it('shows upload and cancel buttons after file selection', async () => {
    render(<DocumentUpload onDocumentReady={mockOnDocumentReady} />)
    
    const file = new File(['content'], 'test.pdf', { type: 'application/pdf' })
    const input = screen.getByRole('button').querySelector('input')
    
    await userEvent.upload(input, file)
    
    await waitFor(() => {
      expect(screen.getByText('Upload Document')).toBeInTheDocument()
      expect(screen.getByText('Cancel')).toBeInTheDocument()
    })
  })

  it('resets state when cancel is clicked', async () => {
    render(<DocumentUpload onDocumentReady={mockOnDocumentReady} />)
    
    const file = new File(['content'], 'test.pdf', { type: 'application/pdf' })
    const input = screen.getByRole('button').querySelector('input')
    
    await userEvent.upload(input, file)
    
    const cancelButton = screen.getByText('Cancel')
    await userEvent.click(cancelButton)
    
    await waitFor(() => {
      expect(screen.getByText(/click to upload or drag and drop/i)).toBeInTheDocument()
    })
  })
})
