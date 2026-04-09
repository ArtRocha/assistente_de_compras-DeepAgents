# Colecoes MongoDB

## store_validation_cache

Documento:
- `cache_key` (string, unico): `<store_normalized>::<domain>`
- `store_name` (string)
- `store_name_normalized` (string)
- `domain` (string)
- `trust_data` (object): payload bruto de validacao
- `created_at` (datetime)
- `updated_at` (datetime)
- `expires_at` (datetime)

Indices:
- unico em `cache_key`
- TTL em `expires_at` com `expireAfterSeconds=0`

## orchestration_events

Documento:
- `event_type` (string)
- `workflow_id` (int|null)
- `payload` (object)
- `created_at` (datetime)

Indice:
- `created_at`
