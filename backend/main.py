from fastapi import FastAPI, HTTPException, Depends, Query
from typing import Optional, List, Dict
import uuid
from datetime import datetime,UTC
from config import get_settings
from models import ContentRequest, ContentResponse, SearchRequest, Contentanalysis
from ai_services import AIService
from cache import CacheService
from vector_store import VectorStore
from dotenv import load_dotenv
import json
import os
from pinecone import ServerlessSpec, Pinecone

# Load environment variables
load_dotenv()

app = FastAPI()
settings = get_settings()

ai_service = AIService(settings.GEMINI_API_KEY)
vector_store = VectorStore()
cache_service = CacheService(settings.REDIS_URL)

@app.post("/content", response_model=ContentResponse)
async def create_content(request: ContentRequest):
    try:
        content_id = str(uuid.uuid4())
        
        analysis = await ai_service.analyze_content(request.text)
        
        embeddings = await ai_service.generate_embeddings(request.text)
        
        # Store embeddings
        await vector_store.store_embeddings(
            content_id,
            embeddings,
            {
                "tenant_id": request.tenant_id,
                "analysis": str(analysis),
                "content": request.text,
                **request.metadata
            }
        )
        current_time = datetime.now(UTC).isoformat()
        # Prepare response
        response = ContentResponse(
            id=content_id,
            text=request.text,
            metadata=request.metadata,
            analysis=analysis,
            created_at=current_time,
            updated_at=current_time
        )
        
        # Cache the response
        await cache_service.set(f"content:{content_id}", response.model_dump()) 
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/content/{content_id}", response_model=Contentanalysis)
async def get_content(content_id: str):
    try:
        #Check cache first
        cached_content = await cache_service.get(f"content:{content_id}")
        if cached_content:
            # Convert analysis dict to string if needed
            analysis_str = json.dumps(cached_content["analysis"]) if isinstance(cached_content["analysis"], dict) else cached_content["analysis"]
            
            return Contentanalysis(
                id=cached_content["id"],
                text=cached_content["text"],
                analysis=analysis_str,
                created_at=cached_content["created_at"],
                updated_at=cached_content["updated_at"]
            )
        pc = Pinecone(
                api_key=os.getenv("PINECONE_API_KEY"), 
                environment="content-embeddings-c9hbhim.svc.aped-4627-b74a.pinecone.io"
            )
        #index_name = "content-embeddings"
        index = pc.Index("content-embeddings")
        response =index.fetch([content_id])
        if response and response.vectors:
            metadata = response.vectors[content_id].metadata
            
            content = metadata.get("content")
            analysis = metadata.get("analysis")
            created_at = metadata.get("created_at")
            updated_at = metadata.get("updated_at")
            
            return Contentanalysis(
                id=content_id,
                text=content,
                #metadata=metadata,
                analysis=analysis,
                created_at=created_at,
                updated_at=updated_at
            )
        
        raise HTTPException(status_code=404, detail="Content not found")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/content/search", response_model=List[Contentanalysis])
async def search_content(request: SearchRequest):
    try:
        pc = Pinecone(
            api_key=os.getenv("PINECONE_API_KEY"),
            host="content-embeddings-c9hbhim.svc.aped-4627-b74a.pinecone.io"
        )
        index = pc.Index("content-embeddings")
        
        embeddings = await ai_service.generate_embeddings(request.query)
        
        filter_conditions = {
            "tenant_id": request.tenant_id
        }
        if request.filters:
            filter_conditions.update(request.filters)
            
        search_response = index.query(
            vector=embeddings,
            top_k=1,
            filter=filter_conditions,
            include_metadata=True
        )

        results = []
        for match in search_response.matches:
            metadata = match.metadata
            analysis_str = json.dumps(metadata.get("analysis")) if isinstance(metadata.get("analysis"), dict) else metadata.get("analysis")
            
            result = Contentanalysis(
                id=match.id,
                text=metadata.get("content"),
                analysis=analysis_str,
                created_at=metadata.get("created_at"),
                updated_at=metadata.get("updated_at")
            )
            results.append(result)
            
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 