"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { applyConfig, getConfigDiff, resetConfig } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"
import { FolderSync as FileSync, RefreshCw, FileCode } from "lucide-react"

interface ConfigManagerProps {
  interfaceName: string
  refreshTrigger: number
}

export function ConfigManager({ interfaceName, refreshTrigger }: ConfigManagerProps) {
  const [diff, setDiff] = useState<string>("")
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const handleApply = async () => {
    try {
      setLoading(true)
      const result = await applyConfig(interfaceName)
      toast({
        title: "Success",
        description: `Config applied to ${result.path}`,
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to apply config",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleReset = async () => {
    try {
      setLoading(true)
      await resetConfig(interfaceName)
      toast({
        title: "Success",
        description: "Config reset from main config file",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to reset config",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleGetDiff = async () => {
    try {
      setLoading(true)
      const result = await getConfigDiff(interfaceName)
      setDiff(result.diff || "No differences found")
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to get diff",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="font-mono text-xl font-semibold">Configuration</h2>
        <p className="text-sm text-muted-foreground">Manage config generation and synchronization</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-border">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <FileSync className="h-4 w-4" />
              Apply
            </CardTitle>
            <CardDescription className="text-xs">Generate final config from folder</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={handleApply} disabled={loading} className="w-full" size="sm">
              Apply Config
            </Button>
          </CardContent>
        </Card>

        <Card className="border-border">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <RefreshCw className="h-4 w-4" />
              Reset
            </CardTitle>
            <CardDescription className="text-xs">Regenerate folder from config</CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              onClick={handleReset}
              disabled={loading}
              className="w-full bg-transparent"
              variant="outline"
              size="sm"
            >
              Reset Config
            </Button>
          </CardContent>
        </Card>

        <Card className="border-border">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <FileCode className="h-4 w-4" />
              Diff
            </CardTitle>
            <CardDescription className="text-xs">Compare folder and config</CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              onClick={handleGetDiff}
              disabled={loading}
              className="w-full bg-transparent"
              variant="outline"
              size="sm"
            >
              Show Diff
            </Button>
          </CardContent>
        </Card>
      </div>

      {diff && (
        <Card className="border-border">
          <CardHeader>
            <CardTitle className="text-base font-mono">Configuration Diff</CardTitle>
            <CardDescription className="text-xs">Differences between folder structure and final config</CardDescription>
          </CardHeader>
          <CardContent>
            <pre className="overflow-x-auto rounded bg-muted p-4 font-mono text-xs leading-relaxed">{diff}</pre>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
