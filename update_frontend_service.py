import re

with open("frontend/src/renderer/src/services/assetService.ts", "r", encoding="utf-8") as f:
    content = f.read()

# Update Asset interface
old_interface = """export interface Asset {
  id: string;
  name: string;
  type: string;
  category: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  created_at: string;
}"""

new_interface = """export interface Asset {
  id: string;
  name: string;
  type: string;
  category: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  created_at: string;
  usage_count?: number;
  is_favorite?: boolean;
  tags?: string[];
  file_hash?: string;
}"""

content = content.replace(old_interface, new_interface)

# Add updateAsset and getAssetUsage
extra_methods = """
  updateAsset: async (id: string, payload: Partial<Asset>): Promise<Asset> => {
    return api.put<Asset>(`/assets/${id}`, payload);
  },

  getAssetUsage: async (id: string): Promise<{templates: any[], projects: any[]}> => {
    return api.get<{templates: any[], projects: any[]}>(`/assets/${id}/usage`);
  },
"""

content = content.replace("deleteAsset: async (id: string): Promise<void> => {", extra_methods + "\n  deleteAsset: async (id: string): Promise<void> => {")

with open("frontend/src/renderer/src/services/assetService.ts", "w", encoding="utf-8") as f:
    f.write(content)
