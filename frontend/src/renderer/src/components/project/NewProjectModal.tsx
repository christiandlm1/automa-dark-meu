import React, { useState } from 'react'
import { Modal } from '../ui/Modal'
import { Input } from '../ui/Input'
import { Button } from '../ui/Button'
import { useToast } from '../../contexts/ToastContext'
import { projectService } from '../../services/projectService'
import { isValidProjectName } from '../../utils/validators'

interface NewProjectModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: (projectId: string) => void
}

export const NewProjectModal: React.FC<NewProjectModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const { showToast } = useToast()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [category, setCategory] = useState('')
  const [path, setPath] = useState('')
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleSelectFolder = async () => {
    try {
      // In Electron, call native openDirectory dialog via preload if registered
      // If not, we just let them type or leave it blank for default path on server
      if (window.api && (window.api as any).openDirectory) {
        const folder = await (window.api as any).openDirectory()
        if (folder) setPath(folder)
      } else {
        showToast('Utilizando pasta padrão do sistema', 'info')
      }
    } catch (err) {
      console.error(err)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validation
    const newErrors: Record<string, string> = {}
    if (!name.trim()) {
      newErrors.name = 'O nome do projeto é obrigatório'
    } else if (!isValidProjectName(name)) {
      newErrors.name = 'Nome inválido (apenas letras, números e espaços)'
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    setErrors({})
    setLoading(true)

    try {
      const project = await projectService.create({
        name: name.trim(),
        description: description.trim() || undefined,
        category: category.trim() || undefined,
        path: path.trim() || undefined
      })

      showToast(`Projeto "${project.name}" criado com sucesso!`, 'success')
      onSuccess(project.id)
      onClose()

      // Reset form
      setName('')
      setDescription('')
      setCategory('')
      setPath('')
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Erro ao criar projeto', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Novo Projeto" size="md">
      <form onSubmit={handleSubmit} className="space-y-5">
        <Input
          label="Nome do Projeto *"
          placeholder="Ex: Edição de Vídeos Curtos"
          value={name}
          onChange={(e) => setName(e.target.value)}
          error={errors.name}
          disabled={loading}
        />

        <Input
          label="Categoria"
          placeholder="Ex: Shorts, Reels, Institucional"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          disabled={loading}
        />

        <div className="flex flex-col gap-1.5 w-full">
          <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono">
            Descrição
          </label>
          <textarea
            className="w-full bg-cyber-bg border border-cyber-border focus:border-neon-green/60 focus:ring-1 focus:ring-neon-green/40 rounded px-3 py-2 text-sm text-white placeholder-gray-600 outline-none transition-all duration-200 font-cyber"
            rows={3}
            placeholder="Descreva o propósito deste projeto..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={loading}
          />
        </div>

        <div className="flex gap-2 items-end">
          <div className="flex-1">
            <Input
              label="Local de Salvamento"
              placeholder="Deixe em branco para usar a pasta padrão"
              value={path}
              onChange={(e) => setPath(e.target.value)}
              disabled={loading}
            />
          </div>
          {window.api && (window.api as any).openDirectory && (
            <Button
              type="button"
              variant="secondary"
              onClick={handleSelectFolder}
              disabled={loading}
              className="px-3 py-2 text-xs"
            >
              Procurar...
            </Button>
          )}
        </div>

        <div className="flex justify-end gap-3 pt-3 border-t border-cyber-border/40">
          <Button type="button" variant="secondary" onClick={onClose} disabled={loading}>
            Cancelar
          </Button>
          <Button type="submit" variant="primary" isLoading={loading}>
            Criar Projeto
          </Button>
        </div>
      </form>
    </Modal>
  )
}
