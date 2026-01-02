"""Modal App and Image definitions - isolated to avoid circular imports."""

import modal

# Modal App
app = modal.App("aiuc")

# Modal Image
image = (
    modal.Image.debian_slim(python_version="3.13")
    .uv_sync()
    .add_local_dir("src", "/root/src")
)
