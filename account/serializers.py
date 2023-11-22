from rest_framework import serializers

from account.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
  password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

  class Meta:
    model = User
    fields = [
      'email',
      'username',
      'name',
      'organization',
      'department',
      'tel',
      'password',
      'password2'
    ]
    extra_kwargs = {
      'password': {'write_only': True}
    }

  def save(self):
    user = User(
      email=self.validated_data['email'],
      username=self.validated_data['username'],
      name=self.validated_data['name'],
      organization=self.validated_data['organization'],
      department=self.validated_data['department'],
      tel=self.validated_data['tel'],
    )

    password = self.validated_data['password']
    password2 = self.validated_data['password2']

    if password != password2:
      raise serializers.ValidationError({'password': 'Password must match.'})

    user.set_password(password)
    user.save()

    return user


class UserUpdateSerializer(serializers.ModelSerializer):
  password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

  class Meta:
    model = User
    fields = (
      'username',
      'email',
      'password',
      'password2',
      'name',
      'organization',
      'department',
      'tel',
    )
    read_only_fields = ('date_created', 'username', 'email', 'name')

  def update(self, instance, validated_data):
    password = validated_data.pop('password', None)

    for (key, value) in validated_data.items():
      setattr(instance, key, value)

    if password is not None:
      instance.set_password(password)
    instance.save()
    return instance
