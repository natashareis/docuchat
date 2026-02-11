import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChatInterface } from '../components/ChatInterface'
import { chatService } from '@/services/api'

vi.mock('@/services/api', () => ({
  chatService: {
    ask: vi.fn(),
  },
}))

describe('ChatInterface', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders chat interface', () => {
    render(<ChatInterface documentId={1} />)
    expect(screen.getByText('Ask questions about your document')).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/ask a question/i)).toBeInTheDocument()
  })

  it('sends message when form is submitted', async () => {
    const mockResponse = {
      answer: 'Test answer',
      session_id: 1,
      sources: [],
    }
    chatService.ask.mockResolvedValue(mockResponse)

    render(<ChatInterface documentId={1} />)
    
    const input = screen.getByPlaceholderText(/ask a question/i)
    const submitButton = screen.getByRole('button')

    await userEvent.type(input, 'Test question')
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(chatService.ask).toHaveBeenCalledWith(1, 'Test question', null)
    })

    await waitFor(() => {
      expect(screen.getByText('Test question')).toBeInTheDocument()
      expect(screen.getByText('Test answer')).toBeInTheDocument()
    })
  })

  it('displays error message on failure', async () => {
    chatService.ask.mockRejectedValue(new Error('API Error'))

    render(<ChatInterface documentId={1} />)
    
    const input = screen.getByPlaceholderText(/ask a question/i)
    const submitButton = screen.getByRole('button')

    await userEvent.type(input, 'Test question')
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/encountered an error/i)).toBeInTheDocument()
    })
  })

  it('disables input while loading', async () => {
    chatService.ask.mockImplementation(() => new Promise(() => {}))

    render(<ChatInterface documentId={1} />)
    
    const input = screen.getByPlaceholderText(/ask a question/i)
    const submitButton = screen.getByRole('button')

    await userEvent.type(input, 'Test question')
    await userEvent.click(submitButton)

    await waitFor(() => {
      expect(input).toBeDisabled()
      expect(submitButton).toBeDisabled()
    })
  })
})
