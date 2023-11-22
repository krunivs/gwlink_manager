from django.contrib.auth import authenticate, logout
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import serializers as rf_serializers
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from account.serializers import UserRegistrationSerializer, UserUpdateSerializer
from account.models import User

import datetime
import logging

logger = logging.getLogger("django.server")


@api_view(['POST', 'GET'])
@permission_classes((IsAuthenticated,))
def registration_and_list_view(request):
  # request.method == 'POST'
  #   사용자 등록
  # request.method == 'GET'
  #   사용자 목록
  if request.method == 'GET':
    context = {'users': []}
    try:
      users = User.objects.all()
      for user in users:
      # if not user.is_admin:
        context['users'].append({
          'username': user.username,
          'name': user.name,
          'organization': user.organization,
          'department': user.department,
          'tel': user.tel,
          'email': user.email,
          'ctime': user.date_created,
        })
      context['error'] = 'no_error'
    except ObjectDoesNotExist:
      logger.warning('Not Found: 해당 사용자 정보를 찾을 수 없음')
      context = {'error': '실패: 해당 사용자 정보를 찾을 수 없음 (Not Found)'}
      return Response(context, status=404)
    logger.info('Success: 유저 목록 조회 완료')
    return Response(context, status=200)

  if request.method == 'POST':
    serializer = UserRegistrationSerializer(data=request.data)
    data = {}
    if serializer.is_valid():
      try:
        user = serializer.save()
      except rf_serializers.ValidationError as error:
        data['error'] = {}
        for e in error.args:
          for key in e.keys():
            data['error'][key] = e.get(key)
            logger.warning(e.get(key))
        return Response(data, status=400)
      data['username'] = user.username
      data['name'] = user.name
      data['organization'] = user.organization
      data['department'] = user.department
      data['tel'] = user.tel
      data['email'] = user.email
      data['ctime'] = user.date_created
      data['error'] = 'no_error'
      logger.info("Success: 사용자 등록 완료")
      return Response(data, status=201)
    else:
      data = {'error': {}}
      for key in serializer.errors.keys():
        data['error'][key] = serializer.errors.get(key)[0]
        logger.info('Bad Request: [\''+key+'\'][\''+data['error'][key].code+'\']')
      return Response(data, status=400)


@api_view(['DELETE', 'PUT', 'GET'])
@permission_classes((IsAuthenticated,))
def details_delete_and_update_view(request, username):
  # request.method == 'DELETE'
  #   사용자 삭제
  # request.method == 'PUT'
  #   사용자 정보 수정
  try:
    user = User.objects.get(username=username)
  except User.DoesNotExist:
    logger.warning('Not Found: 해당 사용자 정보를 찾을 수 없음')
    data = {'error': '실패: 해당 사용자 정보를 찾을 수 없음 (Not Found)'}
    return Response(data, status=404)

  if request.method == 'DELETE':
    operation = user.delete()
    data = {}
    if operation:
      data['username'] = user.username
      data['name'] = user.name
      data['organization'] = user.organization
      data['department'] = user.department
      data['tel'] = user.tel
      data['email'] = user.email
      data['ctime'] = user.date_created
      data['error'] = 'no_error'
      logger.info('Success: 사용자 정보 삭제 완료')
      return Response(data, status=200)
    else:
      logger.warning('Internal Server Error: 사용자 삭제 실패')
      data['error'] = '실패: 시스템 내부 오류 (Internal Server Error)'
      return Response(data, status=500)

  if request.method == 'PUT':
    if User.objects.filter(username=username).exists():
      user = User.objects.get(username=username)
    else:
      logger.warning('Not Found: 해당 사용자 정보를 찾을 수 없음')
      context = {'error': '실패: 해당 사용자 정보를 찾을 수 없음 (Not Found)'}
      return Response(context, status=404)

    if Token.objects.filter(user=request.user).exists():
      if not User.objects.get(username=request.user.username).is_admin:
        if request.user.username != username:
          logger.warning('Unauthorized: 토큰 인증 오류')
          context = {'error': '실패: 토큰 인증 오류 (Unauthorized)'}
          return Response(context, status=401)
    else:
      logger.warning('Unauthorized: 토큰 인증 오류')
      context = {'error': '실패: 토큰 인증 오류 (Unauthorized)'}
      return Response(context, status=401)

    serializer = UserUpdateSerializer(instance=user, data=request.data, partial=True)
    data = {}
    if serializer.is_valid():
      try:
        user = serializer.save()
      except rf_serializers.ValidationError:
        logger.warning('Bad Request: body 파라미터 오류')
        data['error'] = '실패: body 파라미터 오류 (Bad Request)'
        return Response(data, status=400)
      data['username'] = user.username
      data['name'] = user.name
      data['organization'] = user.organization
      data['department'] = user.department
      data['tel'] = user.tel
      data['email'] = user.email
      data['ctime'] = user.date_created
      data['error'] = 'no_error'
      logger.info('Success: 사용자 정보 수정 완료')
      return Response(data, status=200)
    else:
      data = {'error': {}}
      for key in serializer.errors.keys():
        data['error'][key] = serializer.errors.get(key)[0]
        logger.info('Bad Request: [\'' + key + '\'][\'' + serializer.errors.get(key)[0].code + '\']')
      return Response(data, status=400)

  if request.method == 'GET':
    context = {
      'username': user.username,
      'name': user.name,
      'organization': user.organization,
      'department': user.department,
      'tel': user.tel,
      'email': user.email,
      'ctime': user.date_created,
      'error': 'no_error'
    }
    logger.info('Success: 사용자 상세 정보 조회 완료')
    return Response(context, status=200)


@api_view(['POST'])
@permission_classes((AllowAny,))
def login_view(request):
  if request.method == 'POST':
    try:
      user = authenticate(username=request.data['email'], password=request.data['password'])
    except (MultiValueDictKeyError, KeyError):
      logger.warning('Bad Request: body 파라미터 오류')
      context = {'error': 'body 파라미터 오류 (Bad Request)'}
      return Response(context, status=400)
    if user is not None:
      if Token.objects.filter(user=user).exists():
        tz_info = Token.objects.get(user=user).created.tzinfo
        delta = datetime.datetime.now(tz_info) - Token.objects.get(user=user).created
        if delta.days > 7:
          Token.objects.filter(user=user).delete()
          Token.objects.create(user=user)
      else:
        # last login update
        Token.objects.create(user=user)
      token = Token.objects.get(user=user).key
      user.last_login = datetime.datetime.now()
      user.save()
      context = {
        'token_type': 'bearer',
        'access_token': token,
        'error': 'no_error',
      }
      logger.info('Success: 사용자 로그인 완료')
      return Response(context, status=200)
    else:
      context = {
        'error': '실패: 사용자 인증 실패'
      }
      logger.warning('Unauthrized: 사용자 인증 실패')
      return Response(context, status=401)
  else:
    logger.warning('Internal Server Error: 시스템 내부 오류')
    return Response({'error': '시스템 내부 오류 (Internal Server Error)'}, status=500)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def logout_view(request):
  if Token.objects.filter(user=request.user).exists():
    user = User.objects.get(email=Token.objects.get(user=request.user).user)
    user.last_login = datetime.datetime.now()
    user.save()
    context = {'error': 'no_error'}
  else:
    logger.warning('Unauthorized: 웹 세션 토큰 인증 오류')
    context = {'error': '실패: 웹 세션 토큰 인증 오류 (Unauthorized)'}
    return Response(context, status=401)
  logger.info('Success: 사용자 로그아웃 완료')
  return Response(context, status=200)
