# 🚀 Deploy Guide — karaevops AI Chat

## Структура файлов

```
terraform/
├── main.tf                  # Lambda + API Gateway + IAM
├── variables.tf
├── outputs.tf
└── lambda/
    ├── lambda_function.py   # Бэкенд (Claude API)
    └── requirements.txt
```

---

## Шаг 1 — Установить зависимости в lambda/

```bash
cd terraform/lambda
pip install -r requirements.txt -t .
cd ..
```

---

## Шаг 2 — Получить Anthropic API Key

1. Зайди на https://console.anthropic.com
2. API Keys → Create Key
3. Скопируй — покажется только один раз

---

## Шаг 3 — Terraform deploy

```bash
# Инициализация
terraform init

# Передать API key безопасно через переменную окружения
export TF_VAR_anthropic_api_key="sk-ant-ТВОЙ_КЛЮЧ"

# Preview что будет создано
terraform plan

# Deploy!
terraform apply
```

После apply в терминале увидишь:
```
api_url = "https://XXXXX.execute-api.us-east-1.amazonaws.com/prod/chat"
```

---

## Шаг 4 — Обновить виджет

В файле `ai-chat-widget.html` замени одну строку:

```javascript
// Было:
const API_URL = "https://YOUR_API_GATEWAY_URL/chat";

// Стало (вставь свой URL из terraform output):
const API_URL = "https://XXXXX.execute-api.us-east-1.amazonaws.com/prod/chat";
```

---

## Шаг 5 — Добавить виджет на сайт

Открой свой `index.html` и вставь перед `</body>`:

```html
<!-- AI Chat Widget -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<script>
  // Вставь сюда весь JS из ai-chat-widget.html
  // (секцию между <script> и </script>)
</script>

<!-- Вставь сюда HTML виджета (chat-bubble + chat-window divs) -->
<!-- Вставь сюда CSS виджета (секцию <style>) -->
```

---

## Шаг 6 — Upload на S3

```bash
aws s3 cp index.html s3://karaevops.com/ \
  --content-type "text/html" \
  --cache-control "no-cache"

# Если есть CloudFront — инвалидируй кэш
aws cloudfront create-invalidation \
  --distribution-id YOUR_DIST_ID \
  --paths "/*"
```

---

## Стоимость

| Сервис | Стоимость |
|--------|-----------|
| Lambda | Free tier (1M requests/month) |
| API Gateway | Free tier (1M requests/month) |
| Claude API | ~$0.003 за разговор |
| SSM Parameter | Бесплатно |

**Итого: практически бесплатно** при трафике портфолио

---

## Debugging

```bash
# Смотреть логи Lambda в реальном времени
aws logs tail /aws/lambda/karaevops-chat-chat --follow

# Тест напрямую через curl
curl -X POST https://XXXXX.execute-api.us-east-1.amazonaws.com/prod/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "What is Zheenbek good at?"}]}'
```

---

## Cleanup (если нужно удалить всё)

```bash
terraform destroy
```
