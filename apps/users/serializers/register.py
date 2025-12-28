from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)


    class Meta:
       model = CustomUser
       fields = ['username','password','confirm_password']
   
    def validate(self,data):
      if data['password'] != data['confirm_password']:
          raise ValidationError("Passwords do not  match")
      return data
      
    def create(self,validated_data):
       validated_data.pop('confirm_password')      
       user =  CustomUser.objects.create_user(**validated_data)

       return user
    def update(self,user,new_data):
       pass
   #  def validate_username(self,username):
       
   #     # check the username is unique 
           
   #     if CustomUser.objects.filter(username = username).first():
   #        raise ValidationError('Username already Taken') 
   #     return username
    
class RegisterResponseSerializer(serializers.Serializer):
   id = serializers.IntegerField()
   username = serializers.CharField()
   refresh = serializers.CharField()
   access = serializers.CharField()
  