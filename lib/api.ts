const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "/api"

export interface Interface {
  name: string
  public_key: string
  address: string
  listen_port: string
}

export interface Peer {
  name: string
  public_key: string
  allowed_ips: string
  endpoint?: string
}

export interface InterfaceState {
  interface: string
  status: "active" | "inactive" | "not_found"
  message?: string
  peers: Array<{
    public_key: string
    endpoint?: string
    allowed_ips?: string
    latest_handshake?: string
    transfer_rx?: string
    transfer_tx?: string
  }>
}

// Interface APIs
export async function getInterfaces(): Promise<string[]> {
  const res = await fetch(`${API_BASE_URL}/interfaces`)
  if (!res.ok) throw new Error("Failed to fetch interfaces")
  return res.json()
}

export async function getInterface(name: string): Promise<Interface> {
  const res = await fetch(`${API_BASE_URL}/interfaces/${name}`)
  if (!res.ok) throw new Error("Failed to fetch interface")
  return res.json()
}

export async function createInterface(data: {
  name: string
  address?: string
  listen_port?: string
}): Promise<Interface> {
  const res = await fetch(`${API_BASE_URL}/interfaces`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error("Failed to create interface")
  return res.json()
}

export async function updateInterface(
  name: string,
  data: { address?: string; listen_port?: string },
): Promise<{ message: string }> {
  const res = await fetch(`${API_BASE_URL}/interfaces/${name}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error("Failed to update interface")
  return res.json()
}

export async function deleteInterface(name: string): Promise<{ message: string }> {
  const res = await fetch(`${API_BASE_URL}/interfaces/${name}`, {
    method: "DELETE",
  })
  if (!res.ok) throw new Error("Failed to delete interface")
  return res.json()
}

// Peer APIs
export async function getPeers(interfaceName: string): Promise<Peer[]> {
  const res = await fetch(`${API_BASE_URL}/interfaces/${interfaceName}/peers`)
  if (!res.ok) throw new Error("Failed to fetch peers")
  return res.json()
}

export async function createPeer(
  interfaceName: string,
  data: { name: string; allowed_ips?: string; endpoint?: string },
): Promise<Peer> {
  const res = await fetch(`${API_BASE_URL}/interfaces/${interfaceName}/peers`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error("Failed to create peer")
  return res.json()
}

export async function updatePeer(
  interfaceName: string,
  peerName: string,
  data: { allowed_ips?: string; endpoint?: string },
): Promise<{ message: string }> {
  const res = await fetch(`${API_BASE_URL}/interfaces/${interfaceName}/peers/${peerName}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error("Failed to update peer")
  return res.json()
}

export async function deletePeer(interfaceName: string, peerName: string): Promise<{ message: string }> {
  const res = await fetch(`${API_BASE_URL}/interfaces/${interfaceName}/peers/${peerName}`, {
    method: "DELETE",
  })
  if (!res.ok) throw new Error("Failed to delete peer")
  return res.json()
}

// Config APIs
export async function applyConfig(interfaceName: string): Promise<{ message: string; path: string }> {
  const res = await fetch(`${API_BASE_URL}/interfaces/${interfaceName}/config/apply`, { method: "POST" })
  if (!res.ok) throw new Error("Failed to apply config")
  return res.json()
}

export async function resetConfig(interfaceName: string): Promise<{ message: string }> {
  const res = await fetch(`${API_BASE_URL}/interfaces/${interfaceName}/config/reset`, { method: "POST" })
  if (!res.ok) throw new Error("Failed to reset config")
  return res.json()
}

export async function getConfigDiff(interfaceName: string): Promise<{ diff: string }> {
  const res = await fetch(`${API_BASE_URL}/interfaces/${interfaceName}/config/diff`)
  if (!res.ok) throw new Error("Failed to get config diff")
  return res.json()
}

// State APIs
export async function getInterfaceState(interfaceName: string): Promise<InterfaceState> {
  const res = await fetch(`${API_BASE_URL}/interfaces/${interfaceName}/state`)
  if (!res.ok) throw new Error("Failed to get interface state")
  return res.json()
}

export async function getStateDiff(interfaceName: string): Promise<{ diff: string; status: string; message?: string }> {
  const res = await fetch(`${API_BASE_URL}/interfaces/${interfaceName}/state/diff`)
  if (!res.ok) throw new Error("Failed to get state diff")
  return res.json()
}
