"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
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
import { createPeer, deletePeer, getPeers, updatePeer, type Peer } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"
import { Copy, Edit2, Plus, Trash2 } from "lucide-react"
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

interface PeerManagerProps {
  interfaceName: string
  refreshTrigger: number
  onPeerChange: () => void
}

export function PeerManager({ interfaceName, refreshTrigger, onPeerChange }: PeerManagerProps) {
  const [peers, setPeers] = useState<Peer[]>([])
  const [loading, setLoading] = useState(false)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [peerToDelete, setPeerToDelete] = useState<string | null>(null)
  const [peerToEdit, setPeerToEdit] = useState<Peer | null>(null)
  const { toast } = useToast()

  const [createFormData, setCreateFormData] = useState({
    name: "",
    allowed_ips: "10.0.0.2/32",
    endpoint: "",
  })

  const [editFormData, setEditFormData] = useState({
    allowed_ips: "",
    endpoint: "",
  })

  useEffect(() => {
    loadPeers()
  }, [interfaceName, refreshTrigger])

  const loadPeers = async () => {
    try {
      setLoading(true)
      const data = await getPeers(interfaceName)
      setPeers(data)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load peers",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    if (!createFormData.name.trim()) {
      toast({
        title: "Error",
        description: "Peer name is required",
        variant: "destructive",
      })
      return
    }

    try {
      await createPeer(interfaceName, createFormData)
      toast({
        title: "Success",
        description: `Peer ${createFormData.name} created successfully`,
      })
      setCreateDialogOpen(false)
      setCreateFormData({ name: "", allowed_ips: "10.0.0.2/32", endpoint: "" })
      loadPeers()
      onPeerChange()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create peer",
        variant: "destructive",
      })
    }
  }

  const openEditDialog = (peer: Peer) => {
    setPeerToEdit(peer)
    setEditFormData({
      allowed_ips: peer.allowed_ips,
      endpoint: peer.endpoint || "",
    })
    setEditDialogOpen(true)
  }

  const handleEdit = async () => {
    if (!peerToEdit) return

    try {
      await updatePeer(interfaceName, peerToEdit.name, editFormData)
      toast({
        title: "Success",
        description: `Peer ${peerToEdit.name} updated successfully`,
      })
      setEditDialogOpen(false)
      setPeerToEdit(null)
      loadPeers()
      onPeerChange()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update peer",
        variant: "destructive",
      })
    }
  }

  const openDeleteDialog = (name: string) => {
    setPeerToDelete(name)
    setDeleteDialogOpen(true)
  }

  const handleDelete = async () => {
    if (!peerToDelete) return

    try {
      await deletePeer(interfaceName, peerToDelete)
      toast({
        title: "Success",
        description: `Peer ${peerToDelete} deleted successfully`,
      })
      setDeleteDialogOpen(false)
      setPeerToDelete(null)
      loadPeers()
      onPeerChange()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete peer",
        variant: "destructive",
      })
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast({
      title: "Copied",
      description: "Public key copied to clipboard",
    })
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-mono text-xl font-semibold">Peers</h2>
          <p className="text-sm text-muted-foreground">Manage peers for {interfaceName}</p>
        </div>
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              Add Peer
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Peer</DialogTitle>
              <DialogDescription>Create a new peer for {interfaceName}</DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="peer-name">Peer Name</Label>
                <Input
                  id="peer-name"
                  placeholder="peer1"
                  value={createFormData.name}
                  onChange={(e) => setCreateFormData({ ...createFormData, name: e.target.value })}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="allowed-ips">Allowed IPs</Label>
                <Input
                  id="allowed-ips"
                  placeholder="10.0.0.2/32"
                  value={createFormData.allowed_ips}
                  onChange={(e) => setCreateFormData({ ...createFormData, allowed_ips: e.target.value })}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="endpoint">Endpoint (Optional)</Label>
                <Input
                  id="endpoint"
                  placeholder="192.168.1.1:51820"
                  value={createFormData.endpoint}
                  onChange={(e) => setCreateFormData({ ...createFormData, endpoint: e.target.value })}
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
      </div>

      {loading ? (
        <div className="py-8 text-center text-sm text-muted-foreground">Loading peers...</div>
      ) : peers.length === 0 ? (
        <Card className="border-border">
          <CardContent className="py-12">
            <div className="text-center text-sm text-muted-foreground">No peers found. Add one to get started.</div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {peers.map((peer) => (
            <Card key={peer.name} className="border-border">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-base font-mono">{peer.name}</CardTitle>
                    <CardDescription className="mt-1 text-xs">Peer Configuration</CardDescription>
                  </div>
                  <div className="flex gap-1">
                    <Button size="sm" variant="ghost" className="h-8 w-8 p-0" onClick={() => openEditDialog(peer)}>
                      <Edit2 className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="h-8 w-8 p-0"
                      onClick={() => openDeleteDialog(peer.name)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="grid gap-1.5">
                  <div className="text-xs font-medium text-muted-foreground">Public Key</div>
                  <div className="flex items-center gap-2">
                    <code className="flex-1 truncate rounded bg-muted px-2 py-1 font-mono text-xs">
                      {peer.public_key}
                    </code>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="h-7 w-7 p-0"
                      onClick={() => copyToClipboard(peer.public_key)}
                    >
                      <Copy className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>
                <div className="grid gap-1.5">
                  <div className="text-xs font-medium text-muted-foreground">Allowed IPs</div>
                  <code className="rounded bg-muted px-2 py-1 font-mono text-xs">{peer.allowed_ips}</code>
                </div>
                {peer.endpoint && (
                  <div className="grid gap-1.5">
                    <div className="text-xs font-medium text-muted-foreground">Endpoint</div>
                    <code className="rounded bg-muted px-2 py-1 font-mono text-xs">{peer.endpoint}</code>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Peer</DialogTitle>
            <DialogDescription>Update peer configuration for {peerToEdit?.name}</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="edit-allowed-ips">Allowed IPs</Label>
              <Input
                id="edit-allowed-ips"
                placeholder="10.0.0.2/32"
                value={editFormData.allowed_ips}
                onChange={(e) => setEditFormData({ ...editFormData, allowed_ips: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="edit-endpoint">Endpoint (Optional)</Label>
              <Input
                id="edit-endpoint"
                placeholder="192.168.1.1:51820"
                value={editFormData.endpoint}
                onChange={(e) => setEditFormData({ ...editFormData, endpoint: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleEdit}>Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Peer</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <span className="font-mono font-semibold">{peerToDelete}</span>? This
              action cannot be undone.
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
    </div>
  )
}
