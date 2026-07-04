import chromadb

client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(
    name="documents"
)


def get_documents():

    data = collection.get()

    metadatas = data.get("metadatas", [])

    documents = {}

    for meta in metadatas:

        filename = meta["source"]

        if filename not in documents:
            documents[filename] = 0

        documents[filename] += 1

    result = []

    for filename, chunks in documents.items():

        result.append({

            "filename": filename,

            "total_chunks": chunks

        })

    return result


def delete_document(filename):

    data = collection.get()

    ids = []
    metadatas = data.get("metadatas", [])

    for index, meta in enumerate(metadatas):

        if meta["source"] == filename:
            ids.append(data["ids"][index])

    if ids:
        collection.delete(ids=ids)

    return len(ids)