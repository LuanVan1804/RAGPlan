from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec

from app.config import settings

logger = logging.getLogger(__name__)

travel_documents = {
    "paris": """# Paris Travel Guide

Paris, the City of Light, is known for its iconic landmarks, world-class museums, and romantic atmosphere.

## Must-Visit Attractions
- **Eiffel Tower**: Visit during sunset for stunning views. Expect crowds; book tickets online in advance.
- **Louvre Museum**: Home to the Mona Lisa. Best to visit early morning. Allow 3-4 hours minimum.
- **Notre-Dame Cathedral**: Currently under restoration but exterior viewing available.
- **Montmartre**: Charming neighborhood with Sacré-Cœur basilica and artist squares.

## Best Time to Visit
- Spring (April-May): Pleasant weather, 15-18°C
- Summer (June-August): Warm but crowded, 20-25°C
- Fall (September-October): Mild, fewer crowds, 12-17°C
- Winter (November-March): Cold, occasional snow, 3-8°C

## Transportation
- Metro is efficient and cheap (1.90€ per ticket)
- Day pass (Carnet) offers 10 rides at reduced rate
- Buses cover the entire city

## Food & Dining
- Café culture is integral to Parisian life
- Croissants, baguettes, and French cheese are staples
- Budget restaurants: 12-15€, Mid-range: 20-40€, Fine dining: 50-150€+

## Neighborhood Recommendations
- Latin Quarter: Student vibe, budget-friendly
- Marais: Trendy shops, galleries, cafes
- Champs-Élysées: Luxury shopping, expensive dining
- Le Haut Marais: Hipster cafes, street art
""",
    "tokyo": """# Tokyo Travel Guide

Tokyo is a vibrant metropolis blending ancient traditions with cutting-edge modernity.

## Must-Visit Attractions
- **Senso-ji Temple**: Tokyo's oldest temple with iconic red lantern. Free entry.
- **Shibuya Crossing**: World's busiest pedestrian crossing. Best viewed from Starbucks above.
- **Tokyo Tower**: 360° city views. Cost: 900¥ (about 6€)
- **Meiji Shrine**: Peaceful Shinto shrine in forested area. Free entry.
- **Tsukiji Fish Market**: Incredible sushi and fresh seafood at competitive prices.

## Best Time to Visit
- Spring (March-May): Cherry blossom season, 15-20°C
- Summer (June-August): Hot and humid, 25-30°C, many festivals
- Fall (September-November): Comfortable, 15-25°C
- Winter (December-February): Cold, 5-10°C, fewer tourists

## Transportation
- JR Yamanote Line: Circular train connecting major areas
- Suica/Pasmo cards: Rechargeable transit cards accepted everywhere
- English signage common, but learning basic stations is helpful

## Food & Dining
- Ramen: 800-1500¥ ($5-10)
- Sushi restaurants: 2000-5000¥ ($13-33) per person
- Convenience stores: 24/7, affordable options
- Michelin-starred restaurants: Available and many are reasonably priced

## Neighborhood Recommendations
- Shibuya: Young, trendy, shopping
- Shinjuku: Entertainment, nightlife, business district
- Harajuku: Fashion, quirky shops, youth culture
- Asakusa: Traditional, temples, local food
- Ginza: Upscale shopping and dining
""",
    "bali": """# Bali Travel Guide

Bali is Indonesia's cultural and spiritual heart with beautiful beaches and lush temples.

## Must-Visit Attractions
- **Tanah Lot**: Iconic temple perched on sea rock. Entry: 30,000 IDR ($2)
- **Ubud**: Cultural center with rice terraces, art markets, monkey forest
- **Seminyak Beach**: Popular beach with beach clubs and water sports
- **Tirta Empul Temple**: Holy spring water temple for ritual bathing
- **Mount Batur**: Sunrise hike offering panoramic views

## Best Time to Visit
- Dry Season (April-October): Best weather, 28-30°C
- Rainy Season (November-March): Fewer tourists, wet but still warm, 27-32°C

## Transportation
- Scooter rentals: 50,000-100,000 IDR/day ($3-7)
- Taxis and Grab: Affordable ride-sharing app
- Organized tours: Available from hotels and tourism centers

## Food & Dining
- Nasi Goreng (fried rice): 20,000-40,000 IDR
- Street food: Incredibly cheap and delicious
- Warung (local restaurants): Budget meals 15,000-50,000 IDR
- Tourist area restaurants: 100,000-300,000 IDR per meal
- Fresh juices and smoothie bowls: 30,000-60,000 IDR

## Neighborhood Recommendations
- Ubud: Culture, art, hiking, rice fields
- Seminyak: Beach, nightlife, upscale dining
- Sanur: Laid-back beach town, good restaurants
- Jimbaran: Beach clubs, seafood, sunset views
- Kuta: Budget-friendly beach area, backpackers hub
""",
    "new_york": """# New York Travel Guide

NYC never sleeps! The city that never sleeps is home to world-class museums, iconic landmarks, and diverse neighborhoods.

## Must-Visit Attractions
- **Statue of Liberty**: Book tickets to reach the crown. Cost: $24 (ferry + entry)
- **Central Park**: Largest urban park, free to explore. Great for picnics and jogging.
- **Times Square**: Iconic but touristy. Great for photo ops, especially at night.
- **Metropolitan Museum**: World-renowned art museum. Suggested donation: $25
- **Brooklyn Bridge**: Free to walk, stunning views of Manhattan skyline

## Best Time to Visit
- Spring (April-May): Pleasant, flowers blooming, 15-20°C
- Fall (September-October): Crisp air, fewer crowds, 15-25°C
- Summer (June-August): Warm but humid, 25-30°C, many outdoor events
- Winter (December-February): Cold, 0-10°C, holiday decorations

## Transportation
- MTA Subway: Most convenient. MetroCard: $33/week or pay-per-ride ($2.90)
- Buses: Good for specific routes and sightseeing
- Walking: Best way to explore neighborhoods

## Food & Dining
- Pizza slice: $2-4
- Hot dogs: $1-3 from street vendors
- Bagels: $1-2
- Casual restaurants: $12-20 per meal
- Mid-range: $30-60 per person
- Fine dining: $100-300+ per person

## Neighborhood Recommendations
- Manhattan: Midtown (touristy), Lower East Side (trendy), Upper West Side (cultural)
- Brooklyn: Williamsburg (hipster), Park Slope (residential), DUMBO (Instagram-worthy)
- Queens: Diverse, affordable, authentic international food
""",
}


class TravelRAG:
    def __init__(self):
        self.embedding_model = settings.PINECONE_EMBEDDING_MODEL
        self.embedding_dimension = 1536  # text-embedding-3-small
        self.embeddings = OpenAIEmbeddings(
            model=self.embedding_model,
            api_key=settings.OPENAI_API_KEY,
        )
        self.namespace = settings.PINECONE_NAMESPACE
        self.index_name = settings.PINECONE_INDEX_NAME
        self.enabled = bool(settings.PINECONE_API_KEY)
        self.connected = False
        self.index = None

        if self.enabled:
            if not settings.OPENAI_API_KEY:
                raise RuntimeError("OPENAI_API_KEY is required for embedding model text-embedding-3-small.")
            try:
                self.index = self._init_pinecone_index()
                self._verify_connection()
                self._bootstrap_default_documents()
            except Exception as exc:
                raise RuntimeError(f"Failed to initialize Pinecone RAG: {exc}") from exc
        else:
            logger.warning("PINECONE_API_KEY is not set. RAG retrieval from Pinecone is disabled.")

    def _init_pinecone_index(self):
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        index_listing = pc.list_indexes()
        if hasattr(index_listing, "names"):
            existing_indexes = set(index_listing.names())
        else:
            existing_indexes = {
                index.get("name")
                for index in index_listing
                if isinstance(index, dict) and index.get("name")
            }

        def _describe_dimension(index_name: str) -> int | None:
            index_config = pc.describe_index(index_name)
            current_dimension = getattr(index_config, "dimension", None)
            if current_dimension is None and isinstance(index_config, dict):
                current_dimension = index_config.get("dimension")
            return int(current_dimension) if current_dimension else None

        def _create_index(index_name: str):
            pc.create_index(
                name=index_name,
                dimension=self.embedding_dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=settings.PINECONE_CLOUD,
                    region=settings.PINECONE_REGION,
                ),
            )
            logger.info("Created Pinecone index '%s'", index_name)

        if self.index_name not in existing_indexes:
            _create_index(self.index_name)
        else:
            current_dimension = _describe_dimension(self.index_name)
            if current_dimension and current_dimension != self.embedding_dimension:
                compatible_index_name = f"{self.index_name}-{self.embedding_dimension}"
                logger.warning(
                    "Index '%s' has dimension=%s, incompatible with model '%s' (needs %s). "
                    "Switching to '%s'.",
                    self.index_name,
                    current_dimension,
                    self.embedding_model,
                    self.embedding_dimension,
                    compatible_index_name,
                )

                if compatible_index_name not in existing_indexes:
                    _create_index(compatible_index_name)
                else:
                    compatible_dimension = _describe_dimension(compatible_index_name)
                    if compatible_dimension and compatible_dimension != self.embedding_dimension:
                        raise ValueError(
                            f"Pinecone index '{compatible_index_name}' has dimension={compatible_dimension}, "
                            f"but embedding model '{self.embedding_model}' requires dimension={self.embedding_dimension}. "
                            "Please set a fresh PINECONE_INDEX_NAME."
                        )
                self.index_name = compatible_index_name
        return pc.Index(self.index_name)

    def _verify_connection(self):
        if self.index is None:
            raise RuntimeError("Pinecone index client is not initialized.")
        self.index.describe_index_stats()
        self.connected = True
        logger.info(
            "Connected to Pinecone index='%s' namespace='%s' embedding_model='%s'",
            self.index_name,
            self.namespace,
            self.embedding_model,
        )

    def _embed_query(self, text: str) -> list[float]:
        return self.embeddings.embed_query(text)

    def _upsert_document(self, doc_id: str, text: str, metadata: dict[str, Any]):
        if not self.enabled or self.index is None:
            return
        payload_metadata = metadata.copy()
        payload_metadata["content"] = text
        self.index.upsert(
            vectors=[
                {
                    "id": doc_id,
                    "values": self._embed_query(text),
                    "metadata": payload_metadata,
                }
            ],
            namespace=self.namespace,
        )

    def _bootstrap_default_documents(self):
        for destination, content in travel_documents.items():
            doc_id = f"seed:{destination}"
            metadata = {
                "doc_id": doc_id,
                "destination": destination.lower(),
                "category": "travel_guide",
                "source": "seed",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "tags": ["default_seed"],
            }
            self._upsert_document(doc_id, content, metadata)

    def _vector_to_document(self, vector: Any) -> Document:
        if isinstance(vector, dict):
            metadata = vector.get("metadata", {}) or {}
            vector_id = vector.get("id", "unknown")
        else:
            metadata = getattr(vector, "metadata", {}) or {}
            vector_id = getattr(vector, "id", "unknown")

        content = metadata.get("content", "")
        if not metadata.get("doc_id"):
            metadata["doc_id"] = vector_id
        return Document(page_content=content, metadata=metadata)

    def _extract_matches(self, query_result: dict[str, Any]) -> list[Document]:
        matches = query_result.get("matches", []) if isinstance(query_result, dict) else getattr(query_result, "matches", [])
        docs: list[Document] = []
        for match in matches:
            metadata = match.get("metadata", {}) if isinstance(match, dict) else getattr(match, "metadata", {}) or {}
            match_id = match.get("id", "") if isinstance(match, dict) else getattr(match, "id", "")
            if metadata.get("content"):
                metadata.setdefault("doc_id", metadata.get("doc_id", match_id))
                docs.append(Document(page_content=metadata["content"], metadata=metadata))
        return docs

    def query_documents(self, query: str, k: int = 3, destination: str | None = None) -> list[Document]:
        if not self.enabled or not self.connected or self.index is None:
            return []

        query_filter = None
        if destination:
            query_filter = {"destination": {"$eq": destination.lower()}}

        result = self.index.query(
            vector=self._embed_query(query),
            top_k=k,
            include_metadata=True,
            namespace=self.namespace,
            filter=query_filter,
        )
        return self._extract_matches(result)

    def retrieve(self, query: str, k: int = 2) -> str:
        docs = self.query_documents(query, k=k)
        if not docs:
            return "No travel documents found."
        return "\n\n".join(doc.page_content for doc in docs)[:2000]

    def retrieve_by_destination(self, destination: str, k: int = 3) -> str:
        docs = self.query_documents(destination, k=k, destination=destination)
        if not docs:
            return ""
        return "\n\n".join(doc.page_content for doc in docs)[:2000]

    def retrieve_destination_context(self, *, destination: str, query: str, k: int = 3) -> tuple[str, bool]:
        docs = self.query_documents(query=query, k=k, destination=destination)
        if not docs:
            return "", False
        return "\n\n".join(doc.page_content for doc in docs)[:2000], True

    def add_knowledge(self, text: str, metadata: dict[str, Any]) -> str:
        if not self.enabled:
            raise RuntimeError("Pinecone RAG is disabled. Set PINECONE_API_KEY to enable knowledge ingestion.")
        doc_id = str(uuid.uuid4())
        full_metadata = metadata.copy()
        full_metadata["doc_id"] = doc_id
        full_metadata["destination"] = full_metadata.get("destination", "unknown").lower()
        full_metadata.setdefault("category", "travel_guide")
        full_metadata.setdefault("source", "admin_upload")
        full_metadata.setdefault("tags", [])
        full_metadata["created_at"] = datetime.now(timezone.utc).isoformat()
        self._upsert_document(doc_id, text, full_metadata)
        return doc_id

    def get_all_documents(self) -> list[Document]:
        if not self.enabled or not self.connected or self.index is None:
            return []

        try:
            listed = self.index.list(namespace=self.namespace)
            ids: list[str] = []
            for item in listed:
                if isinstance(item, str):
                    ids.append(item)
                    continue
                if isinstance(item, dict):
                    if "id" in item:
                        ids.append(item["id"])
                    elif "ids" in item:
                        ids.extend(item["ids"])
                    continue
                item_ids = getattr(item, "ids", None)
                if item_ids:
                    ids.extend(item_ids)

            if not ids:
                return []

            docs: list[Document] = []
            batch_size = 100
            for i in range(0, len(ids), batch_size):
                batch = ids[i : i + batch_size]
                fetched = self.index.fetch(ids=batch, namespace=self.namespace)
                vectors = fetched.get("vectors", {}) if isinstance(fetched, dict) else getattr(fetched, "vectors", {}) or {}
                for vector in vectors.values():
                    docs.append(self._vector_to_document(vector))
            return docs
        except Exception as exc:
            logger.error("Failed to list documents from Pinecone: %s", exc)
            return []

    def get_document_by_id(self, doc_id: str) -> Document | None:
        if not self.enabled or not self.connected or self.index is None:
            return None
        fetched = self.index.fetch(ids=[doc_id], namespace=self.namespace)
        vectors = fetched.get("vectors", {}) if isinstance(fetched, dict) else getattr(fetched, "vectors", {}) or {}
        vector = vectors.get(doc_id)
        if not vector:
            return None
        return self._vector_to_document(vector)

    def update_knowledge(self, doc_id: str, text: str, metadata: dict[str, Any]) -> Document:
        if not self.enabled:
            raise RuntimeError("Pinecone RAG is disabled. Set PINECONE_API_KEY to enable knowledge updates.")
        full_metadata = metadata.copy()
        full_metadata["doc_id"] = doc_id
        full_metadata["destination"] = full_metadata.get("destination", "unknown").lower()
        full_metadata.setdefault("category", "travel_guide")
        full_metadata.setdefault("source", "admin_upload")
        full_metadata.setdefault("tags", [])
        full_metadata.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        self._upsert_document(doc_id, text, full_metadata)
        return Document(page_content=text, metadata=full_metadata)

    def get_stats(self) -> dict[str, Any]:
        docs = self.get_all_documents()
        destinations: dict[str, int] = {}
        for doc in docs:
            destination = doc.metadata.get("destination", "unknown")
            destinations[destination] = destinations.get(destination, 0) + 1

        return {
            "vector_store_type": "Pinecone",
            "pinecone_index": self.index_name,
            "namespace": self.namespace,
            "enabled": self.enabled,
            "connected": self.connected,
            "embedding_model": self.embedding_model,
            "total_documents": len(docs),
            "destinations_covered": sorted(destinations.keys()),
            "docs_by_destination": destinations,
        }


rag = TravelRAG()
