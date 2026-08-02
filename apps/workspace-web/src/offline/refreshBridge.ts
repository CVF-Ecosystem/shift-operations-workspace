type RefreshOwner = () => Promise<void>;
let owner: RefreshOwner | null = null;

export function registerRefreshOwner(refresh: RefreshOwner): () => void {
  owner = refresh;
  return () => { if (owner === refresh) owner = null; };
}

export async function refreshCurrentConsole(): Promise<void> {
  if (!owner) throw new Error('No active refresh owner');
  await owner();
}
