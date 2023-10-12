from django.urls import path
from .views import AllUsersView, UserCreateView, UserDeleteView, UserExportView, SampleAPIView, watermark_pdf_view


urlpatterns = [
    path('users/', AllUsersView.as_view(), name='user_list'),
    path('users/add/', UserCreateView.as_view(), name='user_add'),
    path('users/delete/<int:pk>/', UserDeleteView.as_view(), name='user_delete'),
    path('users/export/', UserExportView.as_view(), name='user_export'),
    path('sample_api/', SampleAPIView.as_view(), name='sample_api'),
    path('watermark_pdf/',watermark_pdf_view, name='watermark_pdf_view'),


]