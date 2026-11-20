import axios, { AxiosHeaders } from 'axios';
import { describe, expect, it } from 'vitest';
import { getApiError } from './client';

describe('getApiError', () => {
  it('uses the API detail when it is a string', () => {
    const error = new axios.AxiosError('request failed', 'ERR_BAD_REQUEST', undefined, undefined, {
      status: 400,
      statusText: 'Bad Request',
      headers: {},
      config: { headers: new AxiosHeaders() },
      data: { detail: 'Credenciales inválidas' },
    });
    expect(getApiError(error, 'fallback')).toBe('Credenciales inválidas');
  });

  it('returns the fallback for unknown errors', () => {
    expect(getApiError(new Error('unknown'), 'fallback')).toBe('fallback');
  });
});
