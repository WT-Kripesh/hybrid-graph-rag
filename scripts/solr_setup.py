import httpx, json, sys

base = "http://localhost:8983"

resp = httpx.get(f"{base}/solr/hybrid_rag/schema/fieldtypes")
existing_types = {t["name"] for t in resp.json().get("fieldTypes", [])}

if "knn_vector" not in existing_types:
    httpx.post(f"{base}/solr/hybrid_rag/schema", json={
        "add-field-type": [{"name": "knn_vector", "class": "solr.DenseVectorField",
                            "vectorDimension": 768, "similarityFunction": "cosine"}]
    })

schema = json.load(open("src/adapters/solr/schema.json"))
existing = {f["name"] for f in httpx.get(f"{base}/solr/hybrid_rag/schema/fields").json().get("fields", [])}

fields = []
for f in schema:
    if f["name"] not in existing:
        entry = dict(f)
        ftype = entry.pop("type")
        entry["type"] = ftype
        if f["name"] == "embedding":
            entry.pop("dimension", None)
            entry.pop("similarityFunction", None)
            entry.pop("vectorOptimization", None)
        fields.append(entry)

if fields:
    r = httpx.post(f"{base}/solr/hybrid_rag/schema", json={"add-field": fields})
    r.raise_for_status()
    print(f"Schema applied: {len(fields)} fields added.")
else:
    print("Schema already up to date.")

# Verify
ft = httpx.get(f"{base}/solr/hybrid_rag/schema/fieldtypes/knn_vector").json()["fieldType"]
print(f"knn_vector dimension: {ft['vectorDimension']}")
