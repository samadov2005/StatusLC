# API Usage Examples

Comprehensive examples of how to use the StatusLC API.

## Authentication

All requests to protected endpoints require authentication. Use one of these methods:

### Session Authentication (Web Browser)
```bash
# Login
curl -c cookies.txt -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=yourpassword" \
  http://localhost:8000/api-auth/login/

# Make authenticated requests with cookies
curl -b cookies.txt \
  http://localhost:8000/api/students/
```

### Token Authentication (Mobile/API)

1) Obtain token (POST credentials):

```bash
curl -X POST http://localhost/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}'
```

Response:

```json
{"token": "abc123..."}
```

2) Use token for requests (example: get current user info):

```bash
curl http://localhost/api/auth/me/ \
  -H "Authorization: Token abc123..."
```

Response:

```json
{
  "username": "admin",
  "email": "admin@example.com",
  "full_name": "Admin User",
  "is_staff": true,
  "is_superuser": true,
  "role": "admin"
}
```

## Common Tasks

### 1. List All Students

```bash
curl -H "Authorization: Token your-token" \
  "http://localhost:8000/api/students/"
```

Response:
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/students/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "full_name": "John Doe",
      "first_name": "John",
      "last_name": "Doe",
      "phone": "998901234567",
      "parent_phone": "998889876543",
      "group": 2,
      "group_name": "English A1 (Basic) at 18:00:00",
      "user": 3,
      "created_at": "2026-04-15T10:30:00Z",
      "updated_at": "2026-04-18T14:22:00Z"
    }
  ]
}
```

### 2. Get Student Details

```bash
curl -H "Authorization: Token your-token" \
  "http://localhost:8000/api/students/1/"
```

Response:
```json
{
  "id": 1,
  "full_name": "John Doe",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "998901234567",
  "parent_phone": "998889876543",
  "group": 2,
  "group_name": "English A1 (Basic) at 18:00:00",
  "user": 3,
  "created_at": "2026-04-15T10:30:00Z",
  "updated_at": "2026-04-18T14:22:00Z"
}
```

### 3. Check Unpaid Students

```bash
curl -H "Authorization: Token your-token" \
  "http://localhost:8000/api/students/unpaid/?month=2026-04-01"
```

Response:
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 2,
      "full_name": "Jane Smith",
      "first_name": "Jane",
      "last_name": "Smith",
      "phone": "998905555555",
      "parent_phone": "998889999999",
      "group": 1,
      "group_name": "English A2 (Elementary) at 19:00:00",
      "user": 4,
      "created_at": "2026-03-20T09:15:00Z",
      "updated_at": "2026-04-10T16:45:00Z"
    }
  ]
}
```

### 4. Record a Payment

```bash
curl -X POST \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "student": 1,
    "amount": "50000.00",
    "month": "2026-04-01",
    "notes": "Payment received in cash"
  }' \
  "http://localhost:8000/api/payments/"
```

Response (201 Created):
```json
{
  "id": 1,
  "student": 1,
  "student_name": "John Doe",
  "amount": "50000.00",
  "month": "2026-04-01",
  "month_display": "2026-04-01",
  "notes": "Payment received in cash",
  "paid_at": "2026-04-18T14:55:20.123456Z"
}
```

### 5. List Student Payments

```bash
curl -H "Authorization: Token your-token" \
  "http://localhost:8000/api/payments/?student=1"
```

Response:
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "student": 1,
      "student_name": "John Doe",
      "amount": "50000.00",
      "month": "2026-04-01",
      "month_display": "2026-04-01",
      "notes": "Payment received in cash",
      "paid_at": "2026-04-18T14:55:20.123456Z"
    }
  ]
}
```

### 6. View Group Details

```bash
curl -H "Authorization: Token your-token" \
  "http://localhost:8000/api/groups/1/"
```

Response:
```json
{
  "id": 1,
  "name": "English A2",
  "time": "19:00:00",
  "level": "Elementary",
  "teacher": 2,
  "teacher_name": "Sarah Johnson",
  "students_count": 12,
  "created_at": "2026-02-10T08:00:00Z",
  "updated_at": "2026-04-15T11:30:00Z"
}
```

### 7. Get Attendance Records

```bash
curl -H "Authorization: Token your-token" \
  "http://localhost:8000/api/attendances/?group=1&date=2026-04-18"
```

Response:
```json
{
  "count": 12,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "student": 1,
      "student_name": "John Doe",
      "group": 1,
      "group_name": "English A2 (Elementary) at 19:00:00",
      "date": "2026-04-18",
      "present": true,
      "status": "Present",
      "note": "",
      "created_at": "2026-04-18T19:05:00Z",
      "updated_at": "2026-04-18T19:05:00Z"
    },
    {
      "id": 2,
      "student": 2,
      "student_name": "Jane Smith",
      "group": 1,
      "group_name": "English A2 (Elementary) at 19:00:00",
      "date": "2026-04-18",
      "present": false,
      "status": "Absent",
      "note": "Sick leave",
      "created_at": "2026-04-18T19:05:00Z",
      "updated_at": "2026-04-18T19:05:00Z"
    }
  ]
}
```

### 8. Record Attendance

```bash
curl -X POST \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "student": 1,
    "group": 1,
    "date": "2026-04-18",
    "present": true,
    "note": ""
  }' \
  "http://localhost:8000/api/attendances/"
```

Response (201 Created):
```json
{
  "id": 5,
  "student": 1,
  "student_name": "John Doe",
  "group": 1,
  "group_name": "English A2 (Elementary) at 19:00:00",
  "date": "2026-04-18",
  "present": true,
  "status": "Present",
  "note": "",
  "created_at": "2026-04-18T19:10:30.456789Z",
  "updated_at": "2026-04-18T19:10:30.456789Z"
}
```

### 9. Update Student Information

```bash
curl -X PATCH \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "998909999999",
    "group": 3
  }' \
  "http://localhost:8000/api/students/1/"
```

Response (200 OK):
```json
{
  "id": 1,
  "full_name": "John Doe",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "998909999999",
  "parent_phone": "998889876543",
  "group": 3,
  "group_name": "English B1 (Intermediate) at 20:00:00",
  "user": 3,
  "created_at": "2026-04-15T10:30:00Z",
  "updated_at": "2026-04-18T14:25:00Z"
}
```

### 10. Create New Group

(Admin only)

```bash
curl -X POST \
  -H "Authorization: Token admin-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "French A1",
    "time": "17:00",
    "level": "Beginner",
    "teacher": 1
  }' \
  "http://localhost:8000/api/groups/"
```

Response (201 Created):
```json
{
  "id": 5,
  "name": "French A1",
  "time": "17:00:00",
  "level": "Beginner",
  "teacher": 1,
  "teacher_name": "Ahmed Hassan",
  "students_count": 0,
  "created_at": "2026-04-18T15:00:00Z",
  "updated_at": "2026-04-18T15:00:00Z"
}
```

## Filter and Search

### Pagination

Most endpoints support pagination with queryable page size:

```bash
curl -H "Authorization: Token your-token" \
  "http://localhost:8000/api/students/?page=2&limit=10"
```

### Sorting

Endpoints support sorting via the `ordering` parameter:

```bash
# Sort by creation date (descending)
curl -H "Authorization: Token your-token" \
  "http://localhost:8000/api/students/?ordering=-created_at"

# Sort by name (ascending)
curl -H "Authorization: Token your-token" \
  "http://localhost:8000/api/students/?ordering=first_name,last_name"
```

## Error Handling

### 400 Bad Request

```json
{
  "detail": "Provide month parameter as YYYY-MM-DD."
}
```

### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden

```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found

```json
{
  "detail": "Not found."
}
```

## Python Example

Using `requests` library:

```python
import requests
from datetime import date

# Base URL
BASE_URL = "http://localhost:8000/api"
TOKEN = "your-token-here"

# Headers
headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# Get unpaid students
month = date(2026, 4, 1)
response = requests.get(
    f"{BASE_URL}/students/unpaid/",
    params={"month": month.isoformat()},
    headers=headers
)

if response.status_code == 200:
    unpaid_students = response.json()
    print(f"Found {unpaid_students['count']} unpaid students")
    for student in unpaid_students['results']:
        print(f"  - {student['full_name']}: {student['phone']}")

# Record a payment
payment_data = {
    "student": 1,
    "amount": "50000.00",
    "month": month.isoformat(),
    "notes": "Received via mobile transfer"
}

response = requests.post(
    f"{BASE_URL}/payments/",
    json=payment_data,
    headers=headers
)

if response.status_code == 201:
    payment = response.json()
    print(f"Payment recorded: {payment['id']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

## JavaScript/Fetch Example

```javascript
const BASE_URL = "http://localhost:8000/api";
const TOKEN = "your-token-here";

const headers = {
  "Authorization": `Token ${TOKEN}`,
  "Content-Type": "application/json"
};

// Get unpaid students
const month = "2026-04-01";
fetch(`${BASE_URL}/students/unpaid/?month=${month}`, {
  method: "GET",
  headers: headers
})
.then(response => response.json())
.then(data => {
  console.log(`Found ${data.count} unpaid students`);
  data.results.forEach(student => {
    console.log(`  - ${student.full_name}: ${student.phone}`);
  });
})
.catch(error => console.error("Error:", error));

// Record a payment
const paymentData = {
  student: 1,
  amount: "50000.00",
  month: month,
  notes: "Received via mobile transfer"
};

fetch(`${BASE_URL}/payments/`, {
  method: "POST",
  headers: headers,
  body: JSON.stringify(paymentData)
})
.then(response => response.json())
.then(data => console.log("Payment recorded:", data))
.catch(error => console.error("Error:", error));
```

## Rate Limiting

Currently, no rate limiting is configured. For production, consider adding:
- DRF throttling classes
- Nginx rate limiting
- Cloud WAF protection

## API Documentation

Interactive API documentation available at:
- `/api/` - Browsable API root
- `/api/students/` - All API endpoints with their documentation
