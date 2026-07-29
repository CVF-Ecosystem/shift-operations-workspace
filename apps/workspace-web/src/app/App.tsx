import { useState } from 'react';
import { LoginView } from '../features/authentication/LoginView';
import { hasSession } from '../features/authentication/session';
import { OperationsConsole } from './OperationsConsole';

export function App() {
  const [authenticated, setAuthenticated] = useState(() => hasSession());

  if (!authenticated) {
    return <LoginView onAuthenticated={() => setAuthenticated(true)} />;
  }

  return <OperationsConsole onSignedOut={() => setAuthenticated(false)} />;
}
