import { useState } from 'react';
import { LoginView } from '../features/authentication/LoginView';
import { hasSession } from '../features/authentication/session';
import { OperationsConsole } from './OperationsConsole';
import { ConnectivityRuntime } from '../offline/ConnectivityRuntime';

export function App() {
  const [authenticated, setAuthenticated] = useState(() => hasSession());

  if (!authenticated) {
    return <LoginView onAuthenticated={() => setAuthenticated(true)} />;
  }

  const signedOut = () => setAuthenticated(false);
  return <ConnectivityRuntime onSignedOut={signedOut}><OperationsConsole onSignedOut={signedOut} /></ConnectivityRuntime>;
}
