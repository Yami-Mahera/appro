from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['test_database']

# Check users collection
print('Users in database:')
for user in db.users.find():
    print(f"Email: {user.get('email')}, Role: {user.get('role')}, Active: {user.get('active', True)}")

# Close connection
client.close()