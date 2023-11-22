daemonset_list = {
	"name": "etri-west-cls",  # (str) 조회 대상 클러스터 이름
	# (list) 조회 대상 클러스터와 연결된 클러스터 목록
	"id": "123e4567-e89b...",  # (str) 등록된 클러스터에 부여한 uuid
	"daemonsets": [
		{
			"name": "proxy-vlc-http",  # (str) daemonset name
			# (str) daemonset의 상태("Active" 혹은 "NotReady" 혹은 "Terminating")
			"state": "Active",
			# (str) namespace name
			"namespace": "etri",
			# (list) docker image list
			"images": ["nginx:latest", "ubuntu:18.04"],
			# (int) desired
			"desired": 1,
			# (int) current
			"current": 1,
			# (int) ready
			"ready": 1,
			"conditions": [
				{
					"condition": "ContainersReady",  # (str)
					"status": "True",  # (str)
					"message": "",  # (str)
					# (str) 업데이트 시간(yyyy-MM-dd HH:mm:SS)
					"updated": "2021-05-26 23:53:56",
				},
			],
			"stime": "2021-05-26 23:53:56",  # (str) daemonset 실행 시간
		},
	],
	"error": "no_error"  # (str) 에러 텍스트
}

daemonset_detail = {
	"name": "etri-west-cls",  # (str) 조회 대상 클러스터 이름
	# (list) 조회 대상 클러스터와 연결된 클러스터 목록
	"id": "123e4567-e89b...",  # (str) 등록된 클러스터에 부여한 uuid
	"daemonsets": [
		{
			"name": "proxy-vlc-http",  # (str) daemonset name
			# (str) daemonset의 상태("Active" 혹은 "NotReady" 혹은 "Terminating")
			"state": "Active",
			# (str) namespace name
			"namespace": "etri",
			# (list) docker image list
			"images": ["nginx:latest", "ubuntu:18.04"],
			# (int) desired
			"desired": 1,
			# (int) current
			"current": 1,
			# (int) ready
			"ready": 1,
			"conditions": [
				{
					"condition": "ContainersReady",  # (str)
					"status": "True",  # (str)
					"message": "",  # (str)
					# (str) 업데이트 시간(yyyy-MM-dd HH:mm:SS)
					"updated": "2021-05-26 23:53:56",
				},
			],
			"stime": "2021-05-26 23:53:56",  # (str) daemonset 실행 시간
		},
	],
	"error": "no_error"  # (str) 에러 텍스트
}

daemonset_delete = {
	"name": "etri-west-cls",  # (str) 클러스터 이름
	"id": "123e4567-e89b...",  # (str) 클러스터 uuid
	"daemonset": "http-vlc",  # (str) 삭제 daemonset 이름
	"error": "no_error"  # (str) 에러 텍스트
}
