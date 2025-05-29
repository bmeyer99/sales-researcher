from fastapi import FastAPI

app = FastAPI(
    title="Sales Prospect Research Tool API",
    description="API for managing sales prospect research tasks.",
    version="0.1.0"
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Sales Prospect Research Tool API!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Further endpoints will be added in subsequent tasks.