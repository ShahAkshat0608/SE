import uvicorn
import os
import logging

# Try to import the env_loader with different import paths
try:
    from utils.env_loader import load_env_variables
except ImportError:
    try:
        from src.main.utils.env_loader import load_env_variables
    except ImportError:
        # Fallback if imports fail
        def load_env_variables():
            logging.warning("Using fallback environment loader")
            return False

if __name__ == "__main__":
    # Load environment variables
    env_loaded = load_env_variables()
    
    if not env_loaded:
        print("WARNING: Email credentials not properly loaded. Email notifications may not work.")
    
    # Use the full module path for reliability
    module_path = "src.main.main:app"
    # When running directly from src/main directory, use local path
    if os.path.basename(os.getcwd()) == "main":
        module_path = "main:app"
    
    # Run the service
    uvicorn.run(module_path, host="0.0.0.0", port=8004, reload=True) 