deployment_list = {
	"name": "etri-west-cls",  # (str) 조회 대상 클러스터 이름
	# (list) 조회 대상 클러스터와 연결된 클러스터 목록
	"id": "123e4567-e89b...",  # (str) 등록된 클러스터에 부여한 uuid
	"deployments": [
		{
			"name": "proxy-vlc-http",  # (str) deployments name
			# (str) deployment의 상태("Active" 혹은 "NotReady" 혹은 "Terminating")
			"state": "Active",
			# (str) namespace name
			"namespace": "etri",
			# (list) docker image list
			"images": ["nginx:latest", "ubuntu:18.04"],
			# (int) ready replica의 수
			"ready_replicas": 1,
			# (int) total replica의 수
			"replicas": 1,
			# (int) restart replica의 수
			"restart": 1,
			# (list(str)) pod selector 목록
			"selector": ["app:proxy-vlc-http"],
			"conditions": [
				{
					"condition": "ContainersReady",  # (str)
					"status": "True",  # (str)
					"message": "",  # (str)
					# (str) 업데이트 시간(yyyy-MM-dd HH:mm:SS)
					"updated": "2021-05-26 23:53:56",
				},
			],
			"stime": "2021-05-26 23:53:56",  # (str) deployment 실행 시간
		},
	],
	"error": "no_error"  # (str) 에러 텍스트
}

deployment_detail = {
	"name": "etri-west-cls",  # (str) 조회 대상 클러스터 이름
	# (list) 조회 대상 클러스터와 연결된 클러스터 목록
	"id": "123e4567-e89b...",  # (str) 등록된 클러스터에 부여한 uuid
	"deployments": [
		{
			"name": "proxy-vlc-http",  # (str) deployments name
			# (str) deployment의 상태("Active" 혹은 "NotReady" 혹은 "Terminating")
			"state": "Active",
			# (str) namespace name
			"namespace": "etri",
			# (list) docker image list
			"images": ["nginx:latest", "ubuntu:18.04"],
			# (int) ready replica의 수
			"ready_replicas": 1,
			# (int) total replica의 수
			"replicas": 1,
			# (int) restart replica의 수
			"restart": 1,
			# (list(str)) pod selector 목록
			"selector": ["app:proxy-vlc-http"],
			"conditions": [
				{
					"condition": "ContainersReady",  # (str)
					"status": "True",  # (str)
					"message": "",  # (str)
					# (str) 업데이트 시간(yyyy-MM-dd HH:mm:SS)
					"updated": "2021-05-26 23:53:56",
				},
			],
			"stime": "2021-05-26 23:53:56",  # (str) deployment 실행 시간
		},
	],
	"error": "no_error"  # (str) 에러 텍스트
}

deployment_delete = {
	"name": "etri-west-cls",  # (str) 클러스터 이름
	"id": "123e4567-e89b...",  # (str) 클러스터 uuid
	"deployment": "http-vlc",  # (str) 삭제 deployment 이름
	"error": "no_error"  # (str) 에러 텍스트
}
