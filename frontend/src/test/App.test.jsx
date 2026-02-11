import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from '../App'

describe('App', () => {
  it('renders header', () => {
    render(<App />)
    expect(screen.getByText('DocuChat AI')).toBeInTheDocument()
  })

  it('renders document upload initially', () => {
    render(<App />)
    expect(screen.getByText('Upload Document')).toBeInTheDocument()
  })

  it('renders footer', () => {
    render(<App />)
    expect(screen.getByText(/use ai-powered rag to ask questions/i)).toBeInTheDocument()
  })
})
