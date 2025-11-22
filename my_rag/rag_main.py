import chromadb
import uuid

def collection_exists(client, name) -> bool:
    return name in [col.name for col in client.list_collections()]

# client = chromadb.Client()
# collection = client.create_collection(name="policies")

client = chromadb.PersistentClient("./my_rag/chroma")
collection = client.get_or_create_collection(name="policies")

policies = []
with open("my_rag/policies.txt", "r", encoding="utf-8") as f:
    for policy in [ele.rstrip() for ele in f.readlines()]:
        policies.append(policy)


collection.add(
    ids=[str(uuid.uuid4()) for _ in range(len(policies))],
    documents=policies,
    metadatas=[{"line": line} for line in range(len(policies))] # give policy(line) number
)

# print(collection.peek())

results = collection.query(
    query_texts=["what is the HR policy?", "what is the smoking policy?"],
    n_results=2
)
for i, query_results in enumerate(results["documents"]):
    print(f"\nQuery {i}")
    for qr in query_results:
        print(qr)
