"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { getInterfaceState, getStateDiff, type InterfaceState } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"
import { Activity, RefreshCw, FileCode } from "lucide-react"

interface StateManagerProps {
  interfaceName: string
  refreshTrigger: number
}

export function StateManager({ interfaceName, refreshTrigger }: StateManagerProps) {
  const [state, setState] = useState<InterfaceState | null>(null)
  const [diff, setDiff] = useState<string>("")
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    loadState()
  }, [interfaceName, refreshTrigger])

  const loadState = async () => {
    try {
      setLoading(true)
      const data = await getInterfaceState(interfaceName)
      setState(data)
    } catch (error) {
      setState(null)
      toast({
        title: "Info",
        description: "Interface is not active or not found",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleGetDiff = async () => {
    try {
      setLoading(true)
      const result = await getStateDiff(interfaceName)
      setDiff(result.diff || "No differences found")
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to get state diff",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-mono text-xl font-semibold">Interface State</h2>
          <p className="text-sm text-muted-foreground">Live status from WireGuard (wg show)</p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={handleGetDiff}
            disabled={loading}
            variant="outline"
            size="sm"
            className="gap-2 bg-transparent"
          >
            <FileCode className="h-4 w-4" />
            Show Diff
          </Button>
          <Button onClick={loadState} disabled={loading} size="sm" className="gap-2">
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
        </div>
      </div>

      {loading && !state ? (
        <div className="py-8 text-center text-sm text-muted-foreground">Loading state...</div>
      ) : !state ? (
        <Card className="border-border">
          <CardContent className="py-12">
            <div className="text-center">
              <Activity className="mx-auto mb-2 h-8 w-8 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">Interface is not active</p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-mono">{state.interface}</CardTitle>
              <CardDescription className="text-xs">
                {state.peers.length} {state.peers.length === 1 ? "peer" : "peers"} connected
              </CardDescription>
            </CardHeader>
          </Card>

          {state.peers.length > 0 && (
            <div className="grid gap-4">
              {state.peers.map((peer, idx) => (
                <Card key={idx} className="border-border">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base font-mono">Peer {idx + 1}</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3 text-sm">
                    <div className="grid gap-1.5">
                      <div className="text-xs font-medium text-muted-foreground">Public Key</div>
                      <code className="truncate rounded bg-muted px-2 py-1 font-mono text-xs">{peer.public_key}</code>
                    </div>
                    {peer.endpoint && (
                      <div className="grid gap-1.5">
                        <div className="text-xs font-medium text-muted-foreground">Endpoint</div>
                        <code className="rounded bg-muted px-2 py-1 font-mono text-xs">{peer.endpoint}</code>
                      </div>
                    )}
                    {peer.allowed_ips && (
                      <div className="grid gap-1.5">
                        <div className="text-xs font-medium text-muted-foreground">Allowed IPs</div>
                        <code className="rounded bg-muted px-2 py-1 font-mono text-xs">{peer.allowed_ips}</code>
                      </div>
                    )}
                    {peer.latest_handshake && (
                      <div className="grid gap-1.5">
                        <div className="text-xs font-medium text-muted-foreground">Latest Handshake</div>
                        <code className="rounded bg-muted px-2 py-1 font-mono text-xs">{peer.latest_handshake}</code>
                      </div>
                    )}
                    <div className="grid grid-cols-2 gap-3">
                      {peer.transfer_rx && (
                        <div className="grid gap-1.5">
                          <div className="text-xs font-medium text-muted-foreground">RX</div>
                          <code className="rounded bg-muted px-2 py-1 font-mono text-xs">{peer.transfer_rx}</code>
                        </div>
                      )}
                      {peer.transfer_tx && (
                        <div className="grid gap-1.5">
                          <div className="text-xs font-medium text-muted-foreground">TX</div>
                          <code className="rounded bg-muted px-2 py-1 font-mono text-xs">{peer.transfer_tx}</code>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {diff && (
        <Card className="border-border">
          <CardHeader>
            <CardTitle className="text-base font-mono">State vs Config Diff</CardTitle>
            <CardDescription className="text-xs">Differences between live state and config file</CardDescription>
          </CardHeader>
          <CardContent>
            <pre className="overflow-x-auto rounded bg-muted p-4 font-mono text-xs leading-relaxed">{diff}</pre>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
