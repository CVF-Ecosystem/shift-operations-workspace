import { useState, type FormEvent } from 'react';
import { ApiError, login } from '../../services/api';
import { setToken } from './session';

export interface LoginViewProps {
  onAuthenticated: () => void;
}

export function LoginView({ onAuthenticated }: LoginViewProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError(null);
    try {
      const token = await login(username, password);
      setToken(token.access_token);
      setUsername('');
      setPassword('');
      onAuthenticated();
    } catch (cause) {
      setPassword('');
      setError(
        cause instanceof ApiError && cause.kind === 'network'
          ? 'Cannot reach the server. Check your connection and try again.'
          : 'Invalid username or password.'
      );
    } finally {
      setPending(false);
    }
  }

  return (
    <main className="login-view">
      <form onSubmit={handleSubmit} aria-label="Sign in">
        <h1>Operations Console</h1>
        <label htmlFor="username">Username</label>
        <input
          id="username"
          name="username"
          autoComplete="username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          required
        />
        <label htmlFor="password">Password</label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />
        {error && (
          <p role="alert" className="login-view__error">
            {error}
          </p>
        )}
        <button type="submit" disabled={pending}>
          {pending ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
    </main>
  );
}
