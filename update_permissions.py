from vector_store import client, COLLECTION_NAME

# Permissions for our two test documents
DOCUMENT_PERMISSIONS = {
    "name.pdf": ["admin"],
    "test.txt": ["admin", "employee"],
}


def update_permissions():
    offset = None
    updated = 0

    while True:
        points, offset = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )

        for point in points:
            source = point.payload.get("source")

            if source in DOCUMENT_PERMISSIONS:
                client.set_payload(
                    collection_name=COLLECTION_NAME,
                    payload={
                        "allowed_roles": DOCUMENT_PERMISSIONS[source]
                    },
                    points=[point.id],
                )

                updated += 1
                print(f"Updated permissions for: {source}")

        if offset is None:
            break

    print(f"Total chunks updated: {updated}")


if __name__ == "__main__":
    update_permissions()
