import React, { useState, useEffect, useRef } from 'react'
import { assetService, Asset } from '../services/assetService'
import {
  Trash2,
  Upload,
  FileAudio,
  Type,
  Image as ImageIcon,
  Video,
  Star,
  Tag,
  Link
} from 'lucide-react'
import { Card } from '../components/ui/Card'
import { Modal } from '../components/ui/Modal'
import { VirtuosoGrid } from 'react-virtuoso'

export const Assets: React.FC = () => {
  const [assets, setAssets] = useState<Asset[]>([])
  const [activeTab, setActiveTab] = useState<string>('image_background')
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Usage Modal State
  const [usageModalOpen, setUsageModalOpen] = useState(false)
  const [selectedAssetForUsage, setSelectedAssetForUsage] = useState<Asset | null>(null)
  const [assetUsage, setAssetUsage] = useState<{ templates: any[]; projects: any[] }>({
    templates: [],
    projects: []
  })

  const tabs = [
    { id: 'image_background', label: 'Imagens', icon: ImageIcon },
    { id: 'video_background', label: 'V\u00eddeos', icon: Video },
    { id: 'font', label: 'Fontes', icon: Type },
    { id: 'music', label: 'M\u00fasicas', icon: FileAudio }
  ]

  const fetchAssets = async () => {
    try {
      const data = await assetService.getAssets(activeTab)
      setAssets(data)
    } catch (error) {
      console.error('Error fetching assets:', error)
    }
  }

  useEffect(() => {
    fetchAssets()
  }, [activeTab])

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setUploading(true)
      setProgress(0)
      try {
        await assetService.uploadAssets(e.target.files, activeTab, 'Default', (p) => setProgress(p))
        await fetchAssets()
      } catch (error) {
        console.error('Upload failed:', error)
      } finally {
        setUploading(false)
        setProgress(0)
        if (fileInputRef.current) fileInputRef.current.value = ''
      }
    }
  }

  const handleDelete = async (id: string) => {
    if (window.confirm('Tem certeza que deseja excluir este asset?')) {
      try {
        await assetService.deleteAsset(id)
        setAssets(assets.filter((a) => a.id !== id))
      } catch (error) {
        console.error('Error deleting asset:', error)
      }
    }
  }

  const handleToggleFavorite = async (asset: Asset) => {
    try {
      const updated = await assetService.updateAsset(asset.id, { is_favorite: !asset.is_favorite })
      setAssets(assets.map((a) => (a.id === asset.id ? updated : a)))
    } catch (error) {
      console.error('Error toggling favorite:', error)
    }
  }

  const handleShowUsage = async (asset: Asset) => {
    setSelectedAssetForUsage(asset)
    try {
      const usage = await assetService.getAssetUsage(asset.id)
      setAssetUsage(usage)
      setUsageModalOpen(true)
    } catch (error) {
      console.error('Error fetching usage:', error)
    }
  }

  const formatSize = (bytes: number) => {
    return (bytes / 1024 / 1024).toFixed(2) + ' MB'
  }

  return (
    <div className="p-6 h-full flex flex-col">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 shrink-0 mb-6">
        <div>
          <h2 className="text-xl font-bold tracking-wider text-white">Biblioteca de Assets</h2>
          <p className="text-xs font-mono text-gray-500 mt-1 uppercase">
            Gerencie fundos, fontes e m\u00fasicas para seus templates
          </p>
        </div>
        <button
          className="btn btn-primary flex items-center gap-2"
          onClick={handleUploadClick}
          disabled={uploading}
        >
          <Upload size={18} />
          {uploading ? `Enviando... ${progress}%` : 'Importar Assets'}
        </button>
      </div>

      <input
        type="file"
        multiple
        className="hidden"
        ref={fileInputRef}
        onChange={handleFileChange}
      />

      {/* Tabs */}
      <div className="flex border-b border-base-content/10 mb-6">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-3 font-medium text-sm flex items-center gap-2 transition-colors ${
              activeTab === tab.id
                ? 'border-b-2 border-primary text-primary'
                : 'text-base-content/60 hover:text-base-content'
            }`}
          >
            <tab.icon size={16} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Grid */}
      <div className="flex-1 overflow-y-auto min-h-0">
        {assets.length === 0 && !uploading ? (
          <div className="flex flex-col items-center justify-center h-full text-base-content/50">
            <p>Nenhum asset encontrado nesta categoria.</p>
            <button className="btn btn-sm btn-outline mt-4" onClick={handleUploadClick}>
              Importar Agora
            </button>
          </div>
        ) : (
          <VirtuosoGrid
            data={assets}
            className="w-full h-full custom-scrollbar"
            listClassName="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 pb-12"
            itemContent={(_, asset) => (
              <Card key={asset.id} className="overflow-hidden flex flex-col group relative h-full">
                <div className="h-32 bg-base-200 flex items-center justify-center overflow-hidden relative">
                  {asset.type === 'image_background' ? (
                    <div
                      className="w-full h-full bg-cover bg-center"
                      style={{
                        backgroundImage: `url(http://127.0.0.1:8420/assets/${asset.file_path.split('\\').pop()?.split('/').pop()})`
                      }}
                    />
                  ) : asset.type === 'video_background' ? (
                    <Video size={48} className="text-base-content/20" />
                  ) : asset.type === 'font' ? (
                    <Type size={48} className="text-base-content/20" />
                  ) : (
                    <FileAudio size={48} className="text-base-content/20" />
                  )}
                  <button
                    className={`absolute top-2 left-2 p-1.5 rounded-md transition-opacity ${asset.is_favorite ? 'text-yellow-400 opacity-100' : 'text-base-content/50 opacity-0 group-hover:opacity-100 hover:text-yellow-400'}`}
                    onClick={() => handleToggleFavorite(asset)}
                    title={asset.is_favorite ? 'Remover dos favoritos' : 'Favoritar'}
                  >
                    <Star size={16} fill={asset.is_favorite ? 'currentColor' : 'none'} />
                  </button>
                </div>
                <div className="p-3 bg-base-100 flex-1 flex flex-col">
                  <h3 className="text-sm font-medium truncate" title={asset.name}>
                    {asset.name}
                  </h3>
                  <div className="text-xs text-base-content/60 mt-1 flex justify-between items-center">
                    <span>{asset.category || 'Default'}</span>
                    <span>{formatSize(asset.file_size)}</span>
                  </div>

                  <div className="mt-2 flex items-center justify-between border-t border-base-content/10 pt-2">
                    <button
                      className="text-xs text-primary flex items-center gap-1 hover:underline"
                      onClick={() => handleShowUsage(asset)}
                    >
                      <Link size={12} />
                      Usado em: {asset.usage_count || 0}
                    </button>
                    <div className="flex gap-1">
                      {asset.tags && asset.tags.length > 0 && (
                        <div title={asset.tags.join(', ')}>
                          <Tag size={12} className="text-info" />
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                <button
                  className="absolute top-2 right-2 p-1.5 bg-error/90 text-error-content rounded-md opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={() => handleDelete(asset.id)}
                  title="Excluir"
                >
                  <Trash2 size={14} />
                </button>
              </Card>
            )}
          />
        )}
      </div>

      {/* Usado em Modal */}
      <Modal
        isOpen={usageModalOpen}
        onClose={() => setUsageModalOpen(false)}
        title={`Usado em: ${selectedAssetForUsage?.name}`}
      >
        <div className="space-y-4">
          <p className="text-sm">
            Veja onde este asset est\u00e1 sendo utilizado (Templates ou Projetos).
          </p>

          <div>
            <h4 className="font-bold text-white mb-2">Templates ({assetUsage.templates.length})</h4>
            {assetUsage.templates.length === 0 ? (
              <p className="text-xs text-gray-500 italic">Nenhum template utiliza este asset.</p>
            ) : (
              <ul className="list-disc pl-5 space-y-1">
                {assetUsage.templates.map((t) => (
                  <li key={t.id} className="text-sm text-gray-300">
                    {t.name}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div>
            <h4 className="font-bold text-white mb-2">Projetos ({assetUsage.projects.length})</h4>
            {assetUsage.projects.length === 0 ? (
              <p className="text-xs text-gray-500 italic">Nenhum projeto utiliza este asset.</p>
            ) : (
              <ul className="list-disc pl-5 space-y-1">
                {assetUsage.projects.map((p) => (
                  <li key={p.id} className="text-sm text-gray-300">
                    {p.name}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </Modal>
    </div>
  )
}
