from celery import shared_task
from django.core.mail import send_mail
from django.core.mail import EmailMessage

from django.template.loader import render_to_string
from weasyprint import HTML

from sales.models import Client, Voucher


@shared_task
def send_invoice_bill_to_client(client_id, voucher_id):
    client = Client.objects.get(id=client_id)
    client_mail = client.email_address
    invoice = Voucher.objects.get(id=voucher_id)
    company = invoice.branch.company

    subject = "Invoice Bill"
    text_msg = f"Your payment bill for {invoice.created_at.date()} has been generated:"
    text_html = render_to_string('sales/bill/bill_base.html', {'invoice': invoice, 'company': company})

    # Generate PDF
    html = HTML(string=text_html)
    pdf_file = html.write_pdf()

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