// Plaid Link integration using the official Plaid Link library
// We'll load it dynamically to avoid SSR issues

export interface PlaidLinkOptions {
  token: string;
  onSuccess: (publicToken: string, metadata: any) => void;
  onExit?: (err: any, metadata: any) => void;
  onEvent?: (eventName: string, metadata: any) => void;
}

export const loadPlaidScript = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    if (typeof window === 'undefined') {
      resolve();
      return;
    }

    // Check if already loaded
    if (window.Plaid) {
      resolve();
      return;
    }

    const script = document.createElement('script');
    script.src = 'https://cdn.plaid.com/link/v2/stable/link-initialize.js';
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Failed to load Plaid script'));
    document.head.appendChild(script);
  });
};

export const createPlaidLink = async (options: PlaidLinkOptions) => {
  await loadPlaidScript();
  
  if (typeof window === 'undefined' || !window.Plaid) {
    throw new Error('Plaid library not loaded');
  }

  const linkHandler = window.Plaid.create({
    token: options.token,
    onSuccess: options.onSuccess,
    onExit: options.onExit,
    onEvent: options.onEvent,
  });

  return linkHandler;
};

// Extend Window interface
declare global {
  interface Window {
    Plaid: {
      create: (config: any) => {
        open: () => void;
        exit: () => void;
      };
    };
  }
}

