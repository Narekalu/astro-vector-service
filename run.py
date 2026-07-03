"""
Entry point for the Astro Vector Service
Run this file to start the service
"""

import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.environ.get("NODE_ENV") != "production",
        log_level="info"
    )
