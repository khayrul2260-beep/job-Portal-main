from django.contrib import admin
from jobportal.models import *

# Register your models here.
admin.site.register([
  User,
  RecruiterProfileModel,
  SeekerProfileModel,
  CategoryModel,
  JobPostModel,
  ApplyJobModel,
])
