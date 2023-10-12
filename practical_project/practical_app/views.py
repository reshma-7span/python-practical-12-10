from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.views import View
from django.template.loader import get_template
from .models import User, UserInfo
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.generic import ListView

class AllUsersView(View):
    template_name = 'user_list.html'

    def get(self, request):
        # Fetch all users and their details
        users = User.objects.all()
        user_details = []
        for user in users:
            try:
                user_info = UserInfo.objects.get(user=user)
                user_details.append((user, user_info))
            except UserInfo.DoesNotExist:
                user_details.append((user, None))

        return render(request, self.template_name, {'user_details': user_details})


class UserCreateView(View):
    template_name = 'user_form.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        user_email = request.POST.get('user_email')
        password = request.POST.get('password')
        date_of_birth = request.POST.get('date_of_birth')
        mobile = request.POST.get('mobile')
        gender = request.POST.get('gender')
        address = request.POST.get('address')

        try:
            # Check if username or email already exists
            if User.objects.filter(username=username).exists():
                raise ValidationError('Username already exists.')

            if User.objects.filter(user_email=user_email).exists():
                raise ValidationError('Email already exists.')

            # Create and save the user
            user = User.objects.create(username=username, user_email=user_email, password=password)
            user.save()

            # Create and save user details in UserInfo table
            user_info = UserInfo.objects.create(
                user=user,
                date_of_birth=date_of_birth,
                mobile=mobile,
                gender=gender,
                address=address
            )
            user_info.save()

            messages.success(request, 'User and details created successfully.')
            return redirect('user_list')

        except ValidationError as e:
            messages.error(request, str(e))
            return redirect('user_add')


class UserDeleteView(View):

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('user_list')


from io import BytesIO
from reportlab.pdfgen import canvas

class UserExportView(View):
    template_name = 'user_list.html'

    def get(self, request):
        # Create a PDF buffer and a PDF document object to draw on it
        buffer = BytesIO()
        p = canvas.Canvas(buffer)

        # Set up the PDF document
        p.setFont("Helvetica", 12)
        users = User.objects.all()

        # Write the PDF content
        y = 700
        for user in users:
            p.drawString(100, y, f"Username: {user.username}")
            p.drawString(100, y - 20, f"Email: {user.user_email}")
            # Add more fields as needed
            y -= 40

        # Close the PDF object cleanly and we're done
        p.showPage()
        p.save()

        # File response with PDF data
        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="user_list.pdf"'
        response.write(pdf)
        return response



# =============================================statement-2 ============================================
import time
import random
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from .decorators import rate_limit_request


class SampleAPIView(APIView):

    @rate_limit_request(identifier='sample_api', timeout=20, limit=10)
    def get(self, request):
        # Simulate some processing time
        time.sleep(1)

        # Return a JSON response with random data
        data = {
            'random_key1': random.randint(1, 100),
            'random_key2': random.random(),
            'message': 'API response'
        }
        return JsonResponse(data, status=status.HTTP_200_OK)



# =================================================== statement-3 ========================================
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render
import os
import io
from django.conf import settings

def add_watermark(input_pdf, output_pdf, watermark_text):
    # Create PDF reader and writer objects
    pdf_reader = PdfReader(input_pdf)
    pdf_writer = PdfWriter()

    # Create watermark PDF
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(8.5 * 72, 11 * 72))  # Standard letter size in points (1 inch = 72 points)
    can.setFont("Helvetica", 12)
    can.drawString(100, 100, watermark_text)
    can.save()

    packet.seek(0)
    watermark = PdfReader(packet)

    # Add watermark to each page
    for i in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[i]
        page.merge_page(watermark.pages[0])
        pdf_writer.add_page(page)

    # Write the output PDF
    with open(output_pdf, 'wb') as output_file:
        pdf_writer.write(output_file)

def watermark_pdf_view(request):
    if request.method == 'POST' and request.FILES['pdf_file']:
        uploaded_file = request.FILES['pdf_file']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        input_pdf_path = os.path.join(settings.MEDIA_ROOT, filename)

        # Create a watermark
        watermark_text = "Watermark Sample"
        output_pdf_path = os.path.join(settings.MEDIA_ROOT, 'output.pdf')
        add_watermark(input_pdf_path, output_pdf_path, watermark_text)

        # Implement PDF password protection (using PyPDF2)
        pdf_writer = PdfWriter()
        pdf_reader = PdfReader(output_pdf_path)

        for page_num in range(len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[page_num])

        pdf_writer.encrypt("password", "owner_password", use_128bit=True)

        with open(output_pdf_path, 'wb') as output_pdf_file:
            pdf_writer.write(output_pdf_file)

        return HttpResponse("PDF with watermark and password protection saved.")

    return render(request, 'upload_pdf.html')















