from django.db import models 

class User(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=1000)
    username = models.CharField(max_length=1000)
    otp = models.CharField(max_length=1000,null=True,blank=True)
    otp_verified = models.BooleanField(default=False)
    private_key = models.CharField(max_length=1000)

class Index(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    index_id = models.CharField(max_length=1000)
    file_folder_name = models.CharField(max_length=1000)
    last_chat_time = models.DateTimeField(auto_now=True)
    all_files = models.CharField(max_length=10000000,null=True,blank=True)
    all_data = models.TextField(null=True,blank=True)
    chat_type = models.CharField(max_length=1000,null=True,blank=True)
    chat_history = models.JSONField(null=True,blank=True)
