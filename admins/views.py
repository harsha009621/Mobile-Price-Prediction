from django.shortcuts import render,redirect,get_object_or_404
from users.models import Register

 
def admin(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        if username=='admin' and password=='admin':
            return redirect('admin_approval')
    return render(request,'admins/adminlogin.html')
# Admin approval page
def admin_approval(request):
    users = Register.objects.all().order_by('-is_approved', 'id')  # pending users first
    return render(request, 'admins/adminhome.html', {'users': users})

# Approve user
def approve_user(request, user_id):
    user = get_object_or_404(Register, id=user_id)
    user.is_approved = True
    user.save()
    return redirect('admin_approval')

# Reject user
def reject_user(request, user_id):
    user = get_object_or_404(Register, id=user_id)
    user.delete()  # remove rejected user
    return redirect('admin_approval')

# stop approval
def toggle_approval(request, user_id):
    user = get_object_or_404(Register, id=user_id)
    user.is_approved = not user.is_approved
    user.save()
    return redirect('admin_approval')

#user login
