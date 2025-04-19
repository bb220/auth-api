from fastapi.middleware.cors import CORSMiddleware

# Define your trusted origins
origins = [
    "http://localhost:3000",          # Local frontend dev
    #"https://your-frontend.com",       # Production frontend domain
]

def add_cors_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
        allow_headers=["Authorization", "Content-Type"],
    )
