from django.db import models

class Users(models.Model):
    username = models.CharField(max_length=11, primary_key=True)
    password = models.CharField(max_length=300)
    usertype = models.IntegerField()
    def __str__(self):
        return self.username

class Admin(models.Model):
    users = models.OneToOneField(Users, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=15, unique=True)

class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    email = models.CharField(max_length=200)
    room = models.IntegerField()
    computer = models.IntegerField()
    datetime = models.DateTimeField(auto_now=True)
    status = models.IntegerField()
    users = models.ForeignKey(Users, on_delete=models.CASCADE, blank=True, null=True)

class Teacher(models.Model):
    users = models.OneToOneField(Users, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=15, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True ,null=True)

class Document(models.Model):
    link = models.CharField(max_length=300, unique=True)
    updatetime = models.DateTimeField(auto_now=True)
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)

class Notificaion(models.Model):
    title = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    link = models.CharField(max_length=300, unique=True, blank=True, null=True)
    datetime = models.DateTimeField(auto_now=True)
    status = models.IntegerField()
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)

class Instructor(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.CharField(max_length=100)
    work = models.CharField(max_length=200, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

class Violation(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField(null=True)

class Student(models.Model):
    users = models.OneToOneField(Users, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=100)
    classs = models.CharField(max_length=15)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=15, unique=True)
    violation = models.ForeignKey(Violation, on_delete=models.CASCADE, blank=True, null=True)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE,blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)

class Temp(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, primary_key=True)
    cname = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    cphone = models.CharField(max_length=15)
    iname = models.CharField(max_length=100)
    iphone = models.CharField(max_length=15)
    room = models.IntegerField()
    computer = models.IntegerField()
    time = models.DateTimeField(auto_now=True)
    image = models.CharField(max_length=300, unique=True, blank=True)

class Work(models.Model):
    week = models.IntegerField()
    work = models.CharField(max_length=200)
    halfday = models.IntegerField()
    halfdays = models.IntegerField(blank=True, null=True)
    comment = models.CharField(max_length=200, blank=True, null=True)
    status = models.IntegerField()
    fimage = models.CharField(max_length=300)
    image = models.CharField(max_length=300, blank=True, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

class Evaluation(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, primary_key=True)
    i1 = models.IntegerField()
    i2 = models.IntegerField()
    i3 = models.IntegerField()
    i4 = models.IntegerField()
    ii1 = models.IntegerField()
    ii2 = models.IntegerField()
    ii3 = models.IntegerField()
    iii1 = models.IntegerField()
    iii2 = models.IntegerField()
    iii3 = models.IntegerField()
    comment = models.CharField(max_length=200, null=True)
    evalute = models.IntegerField()
    feedback = models.CharField(max_length=200, null=True)
    status = models.IntegerField()
    image = models.CharField(max_length=300)