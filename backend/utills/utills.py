import faker
from database.models import User

generator = faker.Faker()

def generate_fake_user():
    return User(name=generator.name(), email =generator.unique.email(), password = "Tajne123")
