A Django REST API for credit approval system.

## Features

- Customer registration with automatic credit limit calculation
- Loan eligibility checking based on credit score
- Loan creation and management
- Background data ingestion from Excel files
- Dockerized application with PostgreSQL and Redis

### Running the Application

1. Clone the repository
2. Run the application:

```bash
# Build and start all services
docker compose up --build

# Run database migrations
docker compose exec web python manage.py migrate

# Create superuser (optional)
docker compose exec web python manage.py createsuperuser

# Ingest data from Excel files
docker compose exec web python manage.py ingest_data
```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### 1. Register Customer
**POST** `/api/register`

```json
{
    "first_name": "John",
    "last_name": "Doe",
    "age": 30,
    "monthly_income": 50000,
    "phone_number": 9876543210
}
```

### 2. Check Loan Eligibility
**POST** `/api/check-eligibility`

```json
{
    "customer_id": 1,
    "loan_amount": 100000,
    "interest_rate": 10.0,
    "tenure": 12
}
```

### 3. Create Loan
**POST** `/api/create-loan`

```json
{
    "customer_id": 1,
    "loan_amount": 100000,
    "interest_rate": 10.0,
    "tenure": 12
}
```

### 4. View Loan Details
**GET** `/api/view-loan/{loan_id}`

### 5. View Customer Loans
**GET** `/api/view-loans/{customer_id}`

## Credit Score Calculation

The system calculates credit scores based on:
- Past loans paid on time (40% weight)
- Number of loans taken (20% weight)
- Loan activity in current year (20% weight)
- Loan approved volume (20% weight)

## Loan Approval Rules

- Credit score > 50: Approve loan
- Credit score 30-50: Approve with interest rate ≥ 12%
- Credit score 10-30: Approve with interest rate ≥ 16%
- Credit score < 10: Reject loan
- Total EMIs > 50% of salary: Reject loan