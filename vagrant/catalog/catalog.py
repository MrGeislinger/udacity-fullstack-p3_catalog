from sqlalchemy import Column, ForeignKey, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# Category of items in the catalog
class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)

# Items in the catalog
class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    # Limit description so it doesn't take up too much (Twitter's new limit)
    description = Column(String(10000))
    # The date will only include the day (not the hour:minute:second)
    date_added = Column(Date)
    image = Column(String)
    # Can have multiple Category IDs for the same item
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

# We added this serialize function to be able to send JSON objects in a
# serializable format
    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name,
            'category_id': self.category_id,
            'description': self.description,
            # 'date_added': self.date_added,
            'image': self.image
        }


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
