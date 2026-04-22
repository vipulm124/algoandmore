import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import time
import uvicorn


app = FastAPI()

request_tracker={}
RATE_LIMIT=3
WINDOW_SECONDS=60

@app.middleware('http')
async def rate_limit_middleware(request: Request, call_next):
    # skip rate limiting for reset endpoint
    if request.url.path == "/reset":
        return await call_next(request)
    
    
    client_ip = None
    if request.client:
        client_ip = request.client.host
    
    current_time = time.time()

    # Initialize or clean old requests
    if client_ip not in request_tracker:
        request_tracker[client_ip] = []
    
    # Remove request older than the window
    request_tracker[client_ip] = [
        req_time for req_time in request_tracker[client_ip]
        if current_time - req_time < WINDOW_SECONDS
        ]
    
    # Check rate limit
    if len(request_tracker[client_ip]) >= RATE_LIMIT:
        # calculate when the oldest request expires
        oldest_request = min(request_tracker[client_ip])
        retry_after = int(WINDOW_SECONDS - (current_time - oldest_request)) + 1

        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded", "message": f"Try again in {retry_after} seconds"},
            headers={"Retry-After": str(retry_after)}
        )
    
    request_tracker[client_ip].append(current_time)

    response = await call_next(request)
    return response

        

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/api/data")
async def get_data(request: Request):
    if not request.client:
        return []
    
    client_id = request.client.host
    
    request_count = len(request_tracker.get(client_id, []))

    return {
        "data": "Success",
        "request_number": request_count,
        "remaining": RATE_LIMIT - request_count,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/status")
def get_status():
    """Endpoint  that returns 503 with Retry-After as HTTP date"""
    retry_after = datetime.utcnow() + timedelta(seconds=30)

    return JSONResponse(
        status_code= 503,
        content={"error": "Service temporarily unavailable"},
        headers={"Retry-After": retry_after.strftime("%a, %d %b %Y %H:%M:%S GMT")}
    )


@app.get("/reset")
async def reset():
    request_tracker.clear()
    return {"message": "Rate limit counter reset"}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)