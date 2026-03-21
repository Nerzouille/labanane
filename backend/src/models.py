from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base

class Search(Base):
    """Stores the user query and links to its extracted data."""
    __tablename__ = "searches"

    id = Column(Integer, primary_key=True, index=True)
    user_query = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    products = relationship("Product", back_populates="search")
    analyses = relationship("Analysis", back_populates="search")

class Product(Base):
    """Stores a single product's data extracted from a specific source."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    search_id = Column(Integer, ForeignKey("searches.id"))
    source = Column(String, index=True)
    title = Column(String)
    price = Column(String)
    features = Column(JSON)
    url = Column(String)

    search = relationship("Search", back_populates="products")

class Analysis(Base):
    """Stores the LLM-generated market analysis and strategy."""
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    search_id = Column(Integer, ForeignKey("searches.id"))
    market_bilan = Column(Text)
    persona = Column(JSON)
    strategy = Column(Text)

    search = relationship("Search", back_populates="analyses")
