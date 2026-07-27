import re

with open("backend/processing/pipeline/pipeline_manager.py", "r", encoding="utf-8") as f:
    content = f.read()

# We want to remove all the standard nodes: CropNode, ResizeNode, ..., MetadataCleanerNode.
# Then replace them with the NodeFactory implementation.

node_classes = [
    "CropNode", "ResizeNode", "ScaleNode", "ZoomNode", "RotateNode", "MirrorNode",
    "BrightnessNode", "ContrastNode", "SaturationNode", "SharpnessNode", "NoiseReductionNode",
    "FrameRateNode", "BitrateNode", "CodecNode",
    "AudioVolumeNode", "AudioFadeInNode", "AudioFadeOutNode",
    "MetadataCleanerNode"
]

for cls in node_classes:
    pattern = r"class " + cls + r"\(BaseNode\):[\s\S]*?(?=(class |# ---|\Z))"
    content = re.sub(pattern, "", content)

# Also clear empty '# ---' headers if they are just stacked
content = re.sub(r'(# ---[^\n]*\n\s*)+', r'\1', content)

# Now add NodeFactory right before ExportNode
factory_code = """class NodeFactory:
    @staticmethod
    def create_standard_node(ntype: str) -> BaseNode:
        class StandardNode(BaseNode):
            @property
            def node_type(self) -> str:
                return ntype

            async def execute(self, input_path: Path, output_path: Path, config: Dict[str, Any], context: Dict[str, Any]) -> Path:
                context["nodes"].append({"type": self.node_type, "config": config})
                return input_path
        return StandardNode()

"""

content = content.replace("class ExportNode", factory_code + "class ExportNode")

# Update PipelineManager init to use NodeFactory
old_init = """        self._node_classes: Dict[str, BaseNode] = {
            "import": ImportNode(),
            "crop": CropNode(),
            "resize": ResizeNode(),
            "scale": ScaleNode(),
            "zoom": ZoomNode(),
            "rotate": RotateNode(),
            "mirror": MirrorNode(),
            "brightness": BrightnessNode(),
            "contrast": ContrastNode(),
            "saturation": SaturationNode(),
            "sharpness": SharpnessNode(),
            "noisereduction": NoiseReductionNode(),
            "framerate": FrameRateNode(),
            "bitrate": BitrateNode(),
            "codec": CodecNode(),
            "audiovolume": AudioVolumeNode(),
            "audiofadein": AudioFadeInNode(),
            "audiofadeout": AudioFadeOutNode(),
            "metadatacleaner": MetadataCleanerNode(),
            "export": ExportNode(self.ffmpeg_plugin)
        }"""

new_init = """        self._node_classes: Dict[str, BaseNode] = {
            "import": ImportNode(),
            "export": ExportNode(self.ffmpeg_plugin)
        }
        
        standard_types = [
            "crop", "resize", "scale", "zoom", "rotate", "mirror",
            "brightness", "contrast", "saturation", "sharpness", "noisereduction",
            "framerate", "bitrate", "codec", "audiovolume", "audiofadein", 
            "audiofadeout", "metadatacleaner"
        ]
        for t in standard_types:
            self._node_classes[t] = NodeFactory.create_standard_node(t)"""

content = content.replace(old_init, new_init)

with open("backend/processing/pipeline/pipeline_manager.py", "w", encoding="utf-8") as f:
    f.write(content)
