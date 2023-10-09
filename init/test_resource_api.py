from fastapi import FastAPI

app = FastAPI()


@app.get("/system-resources")
async def system_resources():
    result = {
        "All": "1000",
        "Availble":"600",
        "used": "400"
    }
    return result