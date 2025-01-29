const BASE_URL = 'http://localhost:5000'; // Allow dynamic base URL from environment variables

interface FetchClientOptions {
  method?: string;
  headers?: Record<string, string>;
  body?: Record<string, unknown>;
}

/**
 * A wrapper around the Fetch API to handle common configurations and error handling.
 *
 * @param {string} endpoint - The API endpoint.
 * @param {FetchClientOptions} options - Optional configuration for the request (e.g., method, headers, body).
 * @returns {Promise<any>} The parsed JSON response.
 */
export async function fetchClient(endpoint: string, options: FetchClientOptions = {}): Promise<any> {
  const { method = 'GET', headers = {}, body } = options;

  // Default headers, extendable by passing custom headers.
  const config: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    ...(body && { body: JSON.stringify(body) }),
  };

  try {
    const response = await fetch(`${BASE_URL}/${endpoint}`, config);

    // Check for 2xx success status codes
    if (!response.ok) {
      const errorData = await response.json().catch(() => null); // Try to parse error body if available
      throw new Error(
        `API Error: ${response.status} ${response.statusText}\n${errorData ? JSON.stringify(errorData) : ''}`
      );
    }

    // If response is JSON, return the parsed object
    return await response.json();
  } catch (error: unknown) {
    // Handle the error based on its type
    if (error instanceof Error) {
      console.error(`Fetch error: ${error.message}`);
      throw error; // Propagate error for further handling or display
    }
    console.error('Unknown fetch error');
    throw new Error('Unknown fetch error');
  }
}