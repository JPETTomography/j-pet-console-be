from database.database import Base
from typing import Type, Callable
from sqlalchemy.orm import Session

def generate_models( ModelClass: Type[Base], generator_creator: Callable, db:Session=None, amount: int = 10, fake_data: dict=None):
    generator = generator_creator(db)
    if fake_data:
        data = []
        for fake_data_element in fake_data:
            fake_data = next(generator)
            fake_data.update(fake_data_element)
            data.append(fake_data)
    else:
        data = [next(generator) for _ in range(amount)]
    models = [ModelClass(**data_element) for data_element in data]
    return models
