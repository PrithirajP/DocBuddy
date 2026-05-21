from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

os.makedirs("uploads", exist_ok=True)

# Path to the compiled React build
frontend_build_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))

if os.path.exists(frontend_build_path):
    # Mount the assets folder
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_build_path, "assets")), name="assets")
    
    # Catch-all route to serve the React index.html
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_build_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_build_path, "index.html"))
else:
    print("Warning: Frontend build not found. API is running, but UI will not load.")