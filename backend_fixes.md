# Backend Fixes

## 1. Missing Article by ID Endpoint

The GET /api/articles/{article_id} endpoint is missing from the server.py file. This endpoint is needed for the purchase orders system to work correctly.

Add the following code to server.py after the existing article endpoints (around line 443):

```python
@api_router.get("/articles/{article_id}", response_model=Article)
async def get_article(
    article_id: str,
    current_user: User = Depends(get_current_user)
):
    article = await db.articles.find_one({"id": article_id})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return Article(**article)
```

## 2. Reporting API Issues

The reporting API endpoints are returning 500 errors due to issues with the MongoDB aggregation pipelines. Here are the potential issues and fixes:

### 2.1. Fournisseurs Report (line 554)

The issue might be in the aggregation pipeline, particularly in the `$map` operation. Check for:
- Field names that don't match the actual document structure
- Potential null values that cause the aggregation to fail

Potential fix:
```python
# Add null checks to the aggregation pipeline
{
    "$addFields": {
        "total_articles": {"$size": {"$ifNull": ["$articles", []]}},
        "total_commandes": {"$size": {"$ifNull": ["$commandes", []]}},
        "valeur_stock": {
            "$sum": {
                "$map": {
                    "input": {"$ifNull": ["$articles", []]},
                    "as": "article",
                    "in": {
                        "$multiply": [
                            {"$ifNull": ["$$article.stock_actuel", 0]}, 
                            {"$ifNull": ["$$article.prix_unitaire", 0]}
                        ]
                    }
                }
            }
        }
    }
}
```

### 2.2. Articles Report (line 622)

Similar issues might be present in the articles report aggregation pipeline. Check for:
- Proper handling of null values in the `$unwind` operation
- Field names that don't match the actual document structure

### 2.3. Commandes Report (line 694)

The commandes report endpoint returns a 200 status code but fails to return valid data. This might be due to:
- Empty result set that's not properly handled
- JSON serialization issues with date fields

Potential fix:
```python
# Add proper error handling for empty result sets
results = await db.commandes.aggregate(pipeline).to_list(1000)
if not results:
    return []  # Return empty list instead of None
return results
```

## Implementation Steps

1. Add the missing article by ID endpoint
2. Fix the reporting API aggregation pipelines
3. Test the fixes to ensure they resolve the issues