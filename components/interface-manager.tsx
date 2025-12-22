"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { createInterface, deleteInterface, getInterfaces } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"
import { Plus, Trash2 } from "lucide-react"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

interface InterfaceManagerProps {
  selectedInterface: string | null
  onSelectInterface: (name: string | null) => void
  onInterfaceChange: () => void
  refreshTrigger: number
}

export function InterfaceManager({
  selectedInterface,
  onSelectInterface,
  onInterfaceChange,
  refreshTrigger,
}: InterfaceManagerProps) {
  const [interfaces, setInterfaces] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [interfaceToDelete, setInterfaceToDelete] = useState<string | null>(null)
  const { toast } = useToast()

  const [formData, setFormData] = useState({
    name: "",
    address: "10.0.0.1/24",
    listen_port: "51820",
  })

  useEffect(() => {
    loadInterfaces()
  }, [refreshTrigger])

  const loadInterfaces = async () => {
    try {
      setLoading(true)
      const data = await getInterfaces()
      setInterfaces(data)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load interfaces",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    if (!formData.name.trim()) {
      toast({
        title: "Error",
        description: "Interface name is required",
        variant: "destructive",
      })
      return
    }

    try {
      await createInterface(formData)
      toast({
        title: "Success",
        description: `Interface ${formData.name} created successfully`,
      })
      setCreateDialogOpen(false)
      setFormData({ name: "", address: "10.0.0.1/24", listen_port: "51820" })
      loadInterfaces()
      onInterfaceChange()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create interface",
        variant: "destructive",
      })
    }
  }

  const handleDelete = async () => {
    if (!interfaceToDelete) return

    try {
      await deleteInterface(interfaceToDelete)
      toast({
        title: "Success",
        description: `Interface ${interfaceToDelete} deleted successfully`,
      })
      if (selectedInterface === interfaceToDelete) {
        onSelectInterface(null)
      }
      setDeleteDialogOpen(false)
      setInterfaceToDelete(null)
      loadInterfaces()
      onInterfaceChange()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete interface",
        variant: "destructive",
      })
    }
  }

  const openDeleteDialog = (name: string) => {
    setInterfaceToDelete(name)
    setDeleteDialogOpen(true)
  }

  return (
    <Card className="border-border">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="text-lg font-mono">Interfaces</CardTitle>
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button size="sm" className="h-8 gap-2">
              <Plus className="h-4 w-4" />
              New
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Interface</DialogTitle>
              <DialogDescription>Add a new WireGuard interface to your configuration.</DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Interface Name</Label>
                <Input
                  id="name"
                  placeholder="wg0"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="address">Address</Label>
                <Input
                  id="address"
                  placeholder="10.0.0.1/24"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="port">Listen Port</Label>
                <Input
                  id="port"
                  placeholder="51820"
                  value={formData.listen_port}
                  onChange={(e) => setFormData({ ...formData, listen_port: e.target.value })}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreate}>Create</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="py-8 text-center text-sm text-muted-foreground">Loading interfaces...</div>
        ) : interfaces.length === 0 ? (
          <div className="py-8 text-center text-sm text-muted-foreground">
            No interfaces found. Create one to get started.
          </div>
        ) : (
          <div className="space-y-2">
            {interfaces.map((iface) => (
              <div
                key={iface}
                className={`flex items-center justify-between rounded border p-3 transition-colors hover:bg-accent ${
                  selectedInterface === iface ? "border-primary bg-accent" : "border-border"
                }`}
              >
                <button className="flex-1 text-left font-mono text-sm" onClick={() => onSelectInterface(iface)}>
                  {iface}
                </button>
                <Button size="sm" variant="ghost" className="h-8 w-8 p-0" onClick={() => openDeleteDialog(iface)}>
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Interface</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <span className="font-mono font-semibold">{interfaceToDelete}</span>? This
              action cannot be undone and will remove all associated peers.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Card>
  )
}
