from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

class ErrorMessage:
  SERVER_ERROR = {'error': "Internal Server Error"}
  NOT_FOUND = {'error': "Not Found"}
  BAD_REQUEST = {'error': "Bad Request"}
  PARAM_400 = {'error': "실패: 파라미터 오류"}
  CLS_404 = {'error': "실패: 해당 클러스터 정보를 찾을 수 없음"}
  CLS_NS_SV_404 = {'error': "실패: 해당 클러스터, 네임스페이스, 서비스 정보를 찾을 수 없음"}
  USR_404 = {'error': "실패: 해당 사용자 정보를 찾을 수 없음"}
  POD_404 = {'error': "실패: 해당 Pod 정보를 찾을 수 없음"}
  SV_404 = {'error': "실패: 해당 Service 정보를 찾을 수 없음"}
  DEP_404 = {'error': "실패: 해당 Deployment 정보를 찾을 수 없음"}
  DS_404 = {'error': "실패: 해당 Daemonset 정보를 찾을 수 없음"}


class HttpContent:
    @staticmethod
    def read_http_upload_file(request: Request, key):
        """
        read http upload file
        :param request:
        :param key: (str) request body key for file
        :return:
        """
        file_object = request.FILES[key]
        buffer = file_object.read()
        filename = file_object.name
        file_object.close()

        return filename, buffer

class HttpResponse:
    @staticmethod
    def http_return_202_accepted(context):
        """
        http response with HTTP 200 status(ACCEPTED)
        :param context: (dict)
        :return: (rest_framework.response.Response)
        """
        if context is None and type(context) == dict:
            http_body = {
                'error': 'no_error'
            }
        else:
            http_body = context
            http_body['error'] = 'no_error'

        return Response(data=http_body, status=status.HTTP_202_ACCEPTED)

    @staticmethod
    def http_return_201_ok(context):
        """
        http response with HTTP 201(CREATED)
        :param context: (dict)
        :return:
        """
        if context is None and type(context) == dict:
            http_body = {
                'error': 'no_error'
            }
        else:
            http_body = context
            http_body['error'] = 'no_error'

        return Response(data=http_body, status=status.HTTP_201_CREATED)

    @staticmethod
    def http_return_200_ok(context):
        """
        http response with HTTP 200(OK)
        :param context: (dict)
        :return: (rest_framework.response.Response)
        """
        if type(context) != dict:
            http_body = {
                'error': 'no_error'
            }
        else:
            http_body = context
            http_body['error'] = 'no_error'

        return Response(data=http_body, status=status.HTTP_200_OK)

    @staticmethod
    def http_return_400_bad_request(error_message):
        """
        http response with HTTP 400 status(BAD REQUEST)
        :param error_message:
        :return: (rest_framework.response.Response)
        """
        if error_message is None: error_message = ''

        http_body = {
            'error': error_message
        }

        return Response(data=http_body, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def http_return_409_conflict(error_message):
        """
        http response with HTTP 409 status(CONFLICT)
        :param error_message:
        :return: (rest_framework.response.Response)
        """
        if error_message is None: error_message = ''

        http_body = {
            'error': error_message
        }

        return Response(data=http_body, status=status.HTTP_409_CONFLICT)

    @staticmethod
    def http_return_500_internal_server_error(error_message):
        """
        http response with HTTP 500 status(INTERNAL_SERVER_ERROR)
        :param error_message: (str) error message
        :return: (rest_framework.response.Response)
        """
        if error_message is None: error_message = ''

        http_body = {
            'error': error_message
        }

        return Response(data=http_body, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def http_return_503_service_unavailable(error_message):
        """
        http response with HTTP 503 status(SERVICE_UNAVAILABLE)
        :param error_message: (str) error message
        :return: (rest_framework.response.Response)
        """
        if error_message is None: error_message = ''

        http_body = {
            'error': error_message
        }

        return Response(data=http_body, status=status.HTTP_503_SERVICE_UNAVAILABLE)