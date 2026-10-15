"""Nine browse groups over the fine-grained MODEL_CATEGORIES task tags.

Groups are the presentation vocabulary for the site category filter and the
frontier index tables; the task tags in `model-coverage.json` remain the
selection and curation layer. Every MODEL_CATEGORIES key must map into exactly
one group.
"""

CATEGORY_GROUPS = {
    "language": ("Language & coding", "语言与编程",
                 ("general", "coding", "translation")),
    "vision": ("Vision", "视觉理解",
               ("vision", "ocr")),
    "image": ("Image & 3D generation", "图像与 3D 生成",
              ("image", "3d")),
    "video": ("Video generation", "视频生成",
              ("video",)),
    "audio": ("Speech & audio", "语音与音频",
              ("realtime", "audio", "transcription", "speech", "music")),
    "retrieval": ("Embeddings & retrieval", "表征与检索",
                  ("embedding", "reranking")),
    "robotics": ("Robotics & embodied AI", "机器人与具身智能",
                 ("robotics", "navigation", "manipulation", "embodied_reasoning", "virtual_agent")),
    "world": ("World models & simulation", "世界模型与仿真",
              ("world",)),
    "specialized": ("Domain-specific", "专业领域模型",
                    ("science", "medical", "security")),
}

TAG_TO_GROUP = {tag: group for group, (_, _, tags) in CATEGORY_GROUPS.items() for tag in tags}


def model_groups(categories):
    """Group ids for a model's task tags, in group order, deduplicated."""
    found = {TAG_TO_GROUP[tag] for tag in categories if tag in TAG_TO_GROUP}
    return [group for group in CATEGORY_GROUPS if group in found]
