# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating user profiles.
    Supports password hashing and makes password field write-only.
    """
    password = serializers.CharField(write_only=True)  # Ensure password is write-only

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}  # Password is write-only and never returned in response

    def create(self, validated_data):
        """
        Creates a user instance with a hashed password.
        The `create_user` method will hash the password automatically.
        """
        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']  # Automatically hashed by create_user method
        )
        return user

    def update(self, instance, validated_data):
        """
        Update the user instance, especially the password if provided.
        Password is hashed and other fields are updated.
        """
        password = validated_data.pop('password', None)  # Extract password if present

        # Update all other fields (except password)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # If a password was provided, ensure it's hashed before saving
        if password:
            instance.set_password(password)
        
        instance.save()  # Save the updated user instance
        return instance

