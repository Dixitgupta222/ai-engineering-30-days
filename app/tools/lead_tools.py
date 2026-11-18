from app.services.lead_service import analyze_lead

def analyze_customer_lead(message: str, company_size: int) -> dict:
    company_size = int(company_size)

    result = analyze_lead(message, company_size)
    return result