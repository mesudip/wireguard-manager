"use client"

import { useState } from "react"
import { InterfaceManager } from "@/components/interface-manager"
import { PeerManager } from "@/components/peer-manager"
import { ConfigManager } from "@/components/config-manager"
import { StateManager } from "@/components/state-manager"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card } from "@/components/ui/card"

export default function WireGuardDashboard() {
  const [selectedInterface, setSelectedInterface] = useState<string | null>(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const triggerRefresh = () => setRefreshTrigger((prev) => prev + 1)

  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-8">
          <h1 className="font-mono text-3xl font-bold tracking-tight">WireGuard Manager</h1>
          <p className="mt-2 text-sm text-muted-foreground">Manage VPN interfaces, peers, and configurations</p>
        </header>

        <div className="grid gap-6 lg:grid-cols-[300px,1fr]">
          <div>
            <InterfaceManager
              selectedInterface={selectedInterface}
              onSelectInterface={setSelectedInterface}
              onInterfaceChange={triggerRefresh}
              refreshTrigger={refreshTrigger}
            />
          </div>

          <div>
            {selectedInterface ? (
              <Card className="border-border p-6">
                <Tabs defaultValue="peers" className="w-full">
                  <TabsList className="grid w-full grid-cols-3 gap-2">
                    <TabsTrigger value="peers">Peers</TabsTrigger>
                    <TabsTrigger value="config">Config</TabsTrigger>
                    <TabsTrigger value="state">State</TabsTrigger>
                  </TabsList>

                  <TabsContent value="peers" className="mt-6">
                    <PeerManager
                      interfaceName={selectedInterface}
                      refreshTrigger={refreshTrigger}
                      onPeerChange={triggerRefresh}
                    />
                  </TabsContent>

                  <TabsContent value="config" className="mt-6">
                    <ConfigManager interfaceName={selectedInterface} refreshTrigger={refreshTrigger} />
                  </TabsContent>

                  <TabsContent value="state" className="mt-6">
                    <StateManager interfaceName={selectedInterface} refreshTrigger={refreshTrigger} />
                  </TabsContent>
                </Tabs>
              </Card>
            ) : (
              <Card className="flex h-[400px] items-center justify-center border-border p-6">
                <div className="text-center">
                  <p className="text-muted-foreground">Select an interface to manage</p>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
