import { ServerMessageSchema, type ServerMessage } from './workflow-types';

export interface WorkflowCallbacks {
  onMessage: (msg: ServerMessage) => void;
  onStatusChange: (status: 'idle' | 'connecting' | 'open' | 'closed' | 'error') => void;
  onError: (err: string) => void;
}

export interface WorkflowConnection {
  send: (msg: object) => void;
  close: () => void;
}

/**
 * Open a WebSocket connection to the workflow endpoint.
 * Validates all incoming messages with Zod before dispatching.
 * Returns { send, close } — call close() to tear down.
 */
export function createWorkflowConnection(
  url: string,
  callbacks: WorkflowCallbacks,
): WorkflowConnection {
  callbacks.onStatusChange('connecting');
  const ws = new WebSocket(url);
  const pendingMessages: string[] = [];

  ws.addEventListener('open', () => {
    callbacks.onStatusChange('open');
    for (const msg of pendingMessages) {
      ws.send(msg);
    }
    pendingMessages.length = 0;
  });

  ws.addEventListener('message', (event) => {
    let raw: unknown;
    try {
      raw = JSON.parse(event.data as string);
    } catch {
      callbacks.onError(`Failed to parse WS message: ${event.data}`);
      return;
    }

    const result = ServerMessageSchema.safeParse(raw);
    if (!result.success) {
      console.warn('Unknown WS message (Zod parse failed):', raw, result.error.flatten());
      return;
    }
    callbacks.onMessage(result.data);
  });

  ws.addEventListener('error', () => {
    callbacks.onStatusChange('error');
    callbacks.onError('WebSocket connection error.');
  });

  ws.addEventListener('close', () => {
    callbacks.onStatusChange('closed');
  });

  return {
    send: (msg: object) => {
      const payload = JSON.stringify(msg);
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(payload);
      } else if (ws.readyState === WebSocket.CONNECTING) {
        pendingMessages.push(payload);
      }
    },
    close: () => ws.close(),
  };
}
