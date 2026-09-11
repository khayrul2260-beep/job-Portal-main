from django.urls import path
from jobportal.views import *


urlpatterns = [
    path('register/', register_view, name='register_view'),
    path('login/', login_view, name='login_view'),
    path('logout/', logout_view, name='logout_view'),
    
    
    path('', dashboard_view, name='dashboard_view'),
    path('profile-view/', profile_view, name='profile_view'),
    path('update-profile-view/', update_profile_view, name='update_profile_view'),
    
    
    path('browse-job/',browse_job_view, name='browse_job_view'),
    path('post-job/',post_job_view,name='post_job_view'),
    path('update-job/<str:id>/',update_job_view,name='update_job_view'),
    path('delete-job/<str:id>/',delete_job_view,name='delete_job_view'),
    
    
    path('apply-job/<str:id>/',apply_job_view,name='apply_job_view'),
    path('my-applications/',my_application,name='my_application'),
    
    
    path('candidate-list/<str:id>/',candidate_list_view,name='candidate_list_view'),

]



