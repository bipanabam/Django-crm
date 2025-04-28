from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML
from sales.models import Client
import tempfile
from io import BytesIO

EMAIL_HOST_USER = settings.EMAIL_HOST_USER

def send_invoice_bill_to_client(client_id, invoice):
    client = Client.objects.get(id=client_id)
    client_mail = client.email_address
    
    subject = "Invoice Bill"
    text_msg = f"Your payment bill for {invoice.created_at.date()} is as below:"
    text_html = render_to_string('sales/bill/bill_base.html', {'invoice': invoice, 'company': invoice.branch.company})

    # Generate PDF
    pdf_file = generate_pdf(text_html)
    
    # Create the email
    email = EmailMessage(
        subject, 
        text_msg, 
        "info@mbsoftech.com.np", 
        [client_mail]
    )
    email.attach(f'{client.name}_#{invoice.invoice_number}.pdf', pdf_file, 'application/pdf')
    
    try:
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def generate_pdf(html_content):
    """Generate PDF from HTML content"""
    html = HTML(string=html_content)
    pdf_file = html.write_pdf()

    return pdf_file