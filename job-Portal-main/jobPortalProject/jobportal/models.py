from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    
    USER_TYPES = [
        ('Recruiter', 'Recruiter'),
        ('Seeker', 'Seeker'),
    ]
    
    display_name = models.CharField(max_length=200, null=True)
    user_type = models.CharField(choices=USER_TYPES, max_length=20, null=True)
    
    def __str__(self):
      return f'{self.username} - {self.user_type}'



class RecruiterProfileModel(models.Model):
    
    # relation field
    recruiter = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='recruiter_profile',
        null=True
    )
    company_name = models.CharField(max_length=200, null=True)
    address = models.TextField(null=True)
    contact = models.CharField(max_length=20, null=True)
    logo = models.ImageField(upload_to='company_logo', null=True)
    
    created_at = models.DateField(auto_now_add=True, null=True)
    updated_at = models.DateField(auto_now=True, null=True)
    
    def __str__(self):
      return f'{self.company_name}'
  
  

class SeekerProfileModel(models.Model):
    
    # relation field
    seeker = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='seeker_profile',
        null=True
    )
    
    name = models.CharField(max_length=200, null=True)
    address = models.TextField(null=True)
    contact = models.CharField(max_length=20, null=True)
    profile_image = models.ImageField(upload_to='seeker_image', null=True)
    
    skills_set = models.TextField(null=True)
    
    created_at = models.DateField(auto_now_add=True, null=True)
    updated_at = models.DateField(auto_now=True, null=True)
    
    def __str__(self):
      return f'{self.name}'
  
  

# (Title, Number of openings, Category, Job description, Skills set
class CategoryModel(models.Model):
    name = models.CharField(max_length=200, null=True)
    
    def __str__(self):
      return f'{self.name}'


class JobPostModel(models.Model):
    
    # relation field
    posted_by = models.ForeignKey(
        RecruiterProfileModel,
        on_delete=models.CASCADE,
        related_name='job_post_info',
        null=True
    )
    
    title = models.CharField(max_length=200, null=True)
    number_of_openings = models.PositiveIntegerField(null=True)
    category = models.ForeignKey(
        CategoryModel,
        on_delete=models.CASCADE,
        null=True
    )
    description = models.TextField(null=True)
    skills_set = models.TextField(null=True)
    deadline = models.DateField(null=True)
    salary = models.FloatField(null=True)
    
    created_at = models.DateField(auto_now_add=True, null=True)
    updated_at = models.DateField(auto_now=True, null=True)
    
    def __str__(self):
      return f'{self.title}'
    


class ApplyJobModel(models.Model):
    # relation field
    applied_by = models.ForeignKey(
        SeekerProfileModel,
        on_delete=models.CASCADE,
        related_name='applied_by_info',
        null=True
    )
    applied_job = models.ForeignKey(
        JobPostModel,
        on_delete=models.CASCADE,
        related_name='applied_job_info',
        null=True
    )
    resume = models.FileField(upload_to='seeker_resume', null=True)
    applied_at = models.DateField(auto_now_add=True, null=True)
    
    def __str__(self):
      return f'{self.applied_by.name}-{self.applied_job.title}'