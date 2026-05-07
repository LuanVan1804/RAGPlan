from typing import List, Dict, Tuple
from langchain_core.documents import Document
import logging

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
        self.docs = self._create_documents()

    def _create_documents(self) -> List[Document]:
        """Convert travel documents to LangChain documents."""
        docs = []
        for destination, content in travel_documents.items():
            doc = Document(
                page_content=content,
                metadata={"destination": destination, "source": "travel_guide"}
            )
            docs.append(doc)
        return docs

    def _score_document(self, query: str, content: str) -> int:
        """Simple lexical score based on shared words between query and content."""
        query_tokens = {token.strip(".,!?()[]{}:;\"'").lower() for token in query.split() if token.strip()}
        if not query_tokens:
            return 0

        content_tokens = {token.strip(".,!?()[]{}:;\"'").lower() for token in content.split() if token.strip()}
        return len(query_tokens.intersection(content_tokens))

    def retrieve(self, query: str, k: int = 2) -> str:
        """Retrieve relevant travel documents for a query."""
        try:
            logger.info(f"RAG Retrieval: Query = '{query}'")
            scored_docs: List[Tuple[int, Document]] = []
            for doc in self.docs:
                score = self._score_document(query, doc.page_content)
                scored_docs.append((score, doc))
                logger.debug(f"   Document '{doc.metadata['destination']}': score={score}")

            results = [doc for score, doc in sorted(scored_docs, key=lambda item: item[0], reverse=True)[:k] if score > 0]
            if not results:
                logger.warning(f" No documents found for query: {query}")
                return "No travel documents found for this destination."

            logger.info(f"Retrieved {len(results)} documents: {[doc.metadata['destination'] for doc in results]}")
            content = "\n\n".join([doc.page_content for doc in results])
            return content[:1500]
        except Exception as e:
            logger.error(f"RAG Error: {str(e)}")
            return f"Error retrieving documents: {str(e)}"

    def retrieve_by_destination(self, destination: str) -> str:
        """Retrieve travel guide for specific destination."""
        destination_lower = destination.lower()
        for key, content in travel_documents.items():
            if key in destination_lower or destination_lower in key:
                return content[:1000]
        return travel_documents.get("paris", "No guide available.")[:1000]


rag = TravelRAG()
