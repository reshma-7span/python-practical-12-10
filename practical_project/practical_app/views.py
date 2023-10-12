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






