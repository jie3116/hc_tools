from django.urls import path

from human_capital import views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/new/", views.employee_create, name="employee_create"),
    path("employees/<int:pk>/edit/", views.employee_update, name="employee_update"),
    path("employees/<int:pk>/delete/", views.employee_delete, name="employee_delete"),
    path("employees/import/", views.employee_import, name="employee_import"),
    path("policies/chat/", views.policy_chat, name="policy_chat"),
    path("assets/", views.assets, name="assets"),
    path("letters/", views.letter_request_list, name="letter_request_list"),
    path("letters/new/", views.letter_request_create, name="letter_request_create"),
    path("letters/<int:pk>/admin-review/", views.letter_request_admin_review, name="letter_request_admin_review"),
    path("letters/<int:pk>/approver-review/", views.letter_request_approver_review, name="letter_request_approver_review"),
    path("api/employees/", views.EmployeeListCreateApi.as_view(), name="api_employees"),
    path("api/policies/", views.PolicyListCreateApi.as_view(), name="api_policies"),
    path("api/templates/", views.TemplateListCreateApi.as_view(), name="api_templates"),
    path("api/requests/", views.LetterRequestListCreateApi.as_view(), name="api_requests"),
    path("api/chatbot/", views.PolicyChatApi.as_view(), name="api_chatbot"),
]
