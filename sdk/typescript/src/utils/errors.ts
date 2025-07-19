/**
 * Error handling utilities for GENESIS SDK
 */

import { AxiosError } from 'axios'

export class GenesisAPIError extends Error {
  code: string
  status?: number
  details?: any

  constructor(message: string, code: string, status?: number, details?: any) {
    super(message)
    this.name = 'GenesisAPIError'
    this.code = code
    this.status = status
    this.details = details
  }
}

export function handleAxiosError(error: AxiosError): GenesisAPIError {
  if (error.response) {
    // Server responded with error
    const data = error.response.data as any
    return new GenesisAPIError(
      data?.message || error.message,
      data?.code || 'API_ERROR',
      error.response.status,
      data?.details
    )
  } else if (error.request) {
    // Request made but no response
    return new GenesisAPIError(
      'No response from server',
      'NETWORK_ERROR',
      undefined,
      { originalError: error.message }
    )
  } else {
    // Something else happened
    return new GenesisAPIError(
      error.message,
      'REQUEST_ERROR',
      undefined,
      { originalError: error }
    )
  }
}

export function isGenesisError(error: any): error is GenesisAPIError {
  return error instanceof GenesisAPIError
}