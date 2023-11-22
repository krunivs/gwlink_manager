namespaces_list = {
  "name": "etri-west-cls",  # (str) 조회 대상 클러스터 이름
  "id": "123e4567-e89b...",  # (str) 등록된 클러스터에 부여한 uuid
  "namespaces": [
    {
      "name": "kubernetes",  # (str) 네임스페이스 이름
      # (str) namespace의 상태("Active" 혹은 "NotReady" 혹은 "Terminating")
      "state": "Active",
      # (list) namespace conditions
      "conditions": [
        {
          "condition": "",  # (str)
          "status": "",  # (str)
          "message": "",  # (str)
          # (str) 업데이트 시간(yyyy-MM-dd HH:mm:SS)
          "updated": "",
        },
      ],
      "stime": "2021-05-26 23:53:56",  # (str) namespace 생성 시간
    },
    {
      "name": "kubernetes222",  # (str) 네임스페이스 이름
      # (str) namespace의 상태("Active" 혹은 "NotReady" 혹은 "Terminating")
      "state": "Active",
      # (list) namespace conditions
      "conditions": [
        {
          "condition": "",  # (str)
          "status": "",  # (str)
          "message": "",  # (str)
          # (str) 업데이트 시간(yyyy-MM-dd HH:mm:SS)
          "updated": "",
        },
      ],
      "stime": "2021-05-26 23:53:56",  # (str) namespace 생성 시간
    },
  ],
  "error": "no_error"  # (str) 에러 텍스트
}

pod_list = {
  "name": "etri-west-cls",  # (str) 조회 대상 클러스터 이름
  # (list) 조회 대상 클러스터와 연결된 클러스터 목록
  "id": "123e4567-e89b...",  # (str) 등록된 클러스터에 부여한 uuid
  "pods": [
    {
      "name": "proxy-vlc-http-57fc8d4b-vxt8",  # (str) pod name
      # (str) pod의 상태(“Running" 혹은 ”Pending" 혹은 “Succeeded" 혹은 ”Failed")
      "state": "Running",
      # (str) namespace name
      "namespace": "etri",
      # (str) labels
      "labels": ["app=proxy-vlc-http", "component=vlc"],
      "host_ip": "10.0.0.206",  # (str) node ip
      "node": "west.worker.com",  # (str) node hostname
      "pod_ip": "10.244.1.75",  # (str) pod ip
      # (list) pod conditions
      "conditions": [
        {
          "condition": "ContainersReady",  # (str)
          "status": "True",  # (str)
          "message": "",  # (str)
          # (str) 업데이트 시간(yyyy-MM-dd HH:mm:SS)
          "updated": "2022-11-30 10:53:56",
        },
        {
          "condition": "ContainersReady2",  # (str)
          "status": "True",  # (str)
          "message": "[ErrImagePullBackoff] Error response from daemon: unauthorized: access to the requested resource ...",
          # (str)
          # (str) 업데이트 시간(yyyy-MM-dd HH:mm:SS)
          "updated": "2022-11-29 23:53:56",
        },
      ],
      # (list) docker image list
      "images": ["nginx:latest", "ubuntu:18.04"],
      "stime": "2022-11-29 11:53:56",  # (str) pod 시작 시간
    },
    {
      "name": "vlc-http-78f594c7c-cm7sf",  # (str) pod name
      # (str) pod의 상태(“Running" 혹은 ”Pending" 혹은 “Succeeded" 혹은 ”Failed")
      "state": "Pending",
      # (str) namespace name
      "namespace": "etri",
      # (str) labels
      "labels": ["app=proxy-vlc-http", "component=vlc"],
      "host_ip": "10.0.0.206",  # (str) node ip
      "node": "west.worker.com",  # (str) node hostname
      "pod_ip": "10.244.1.77",  # (str) pod ip
      # (list) pod conditions
      "conditions": [
        {
          "condition": "ContainersReady",  # (str)
          "status": "True",  # (str)
          "message": "",  # (str)
          # (str) 업데이트 시간(yyyy-MM-dd HH:mm:SS)
          "updated": "2021-05-26 23:53:56",
        },
      ],
      # (list) docker image list
      "images": ["nginx:latest", "ubuntu:18.04"],
      "stime": "2022-11-26 23:53:56",  # (str) pod 시작 시간
    },
    {
      "name": "vlc-http-78f594c7c-345df-gd3d",  # (str) pod name
      # (str) pod의 상태(“Running" 혹은 ”Pending" 혹은 “Succeeded" 혹은 ”Failed")
      "state": "Succeeded",
      # (str) namespace name
      "namespace": "etri",
      # (str) labels
      "labels": ["app=proxy-vlc-http", "component=vlc"],
      "host_ip": "10.0.0.206",  # (str) node ip
      "node": "west.worker.com",  # (str) node hostname
      "pod_ip": "10.244.1.75",  # (str) pod ip
      # (list) pod conditions
      "conditions": [
        {
          "condition": "ContainersReady",  # (str)
          "status": "True",  # (str)
          "message": "",  # (str)
          # (str) 업데이트 시간(yyyy-MM-dd HH:mm:SS)
          "updated": "2021-05-26 23:53:56",
        },
      ],
      # (list) docker image list
      "images": ["nginx:latest", "ubuntu:18.04"],
      "stime": "2022-05-26 23:53:56",  # (str) pod 시작 시간
    },
  ],
  "error": "no_error"  # (str) 에러 텍스트
}

pod_search = {
  "name": "etri-west-cls",  # (str) 요청 pod가 상주하는 클러스터 이름
  "id": "123e4567-e89b...",  # (str) 등록된 클러스터에 부여한 uuid
  "pods": [
    {
      "name": "proxy-vlc-http-57fc8d4b-vxt8",  # (str) pod name
      # (str) pod의 상태(“Running" 혹은 ”Pending" 혹은 “Succeeded" 혹은 ”Failed")
      "state": "Running",
      # (str) namespace name
      "namespace": "etri",
      # (str) labels
      "labels": ["app=proxy-vlc-http", "component=vlc"],
      "host_ip": "10.0.0.206",  # (str) node ip
      "node": "west.worker.com",  # (str) node hostname
      "pod_ip": "10.244.1.75",  # (str) pod ip
      # (list) pod conditions
      "conditions": [
        {
          "condition": "ContainersReady",  # (str)
          "status": "True",  # (str)
          "message": "",  # (str)
          # (str) 업데이트 시간(yyyy-MM-dd HH:mm:SS)
          "updated": "2021-05-26 23:53:56",
        },
      ],
      # (list) docker image list
      "images": ["nginx:latest", "ubuntu:18.04"],
      "stime": "2021-05-26 23:53:56",  # (str) pod 시작 시간
    },
  ],
  "error": "no_error"  # (str) 에러 텍스트
}

pod_detail = {
  "name": "etri-west-cls",  # (str) 요청 pod가 상주하는 클러스터 이름
  "id": "123e4567-e89b...",  # (str) 등록된 클러스터에 부여한 uuid
  "pods": [
    {
      "name": "proxy-vlc-http-57fc8d4b-vxt8",  # (str) pod name
      # (str) pod의 상태(“Running" 혹은 ”Pending" 혹은 “Succeeded" 혹은 ”Failed")
      "state": "Running",
      # (str) namespace name
      "namespace": "etri",
      # (str) labels
      "labels": ["app=proxy-vlc-http", "component=vlc"],
      "host_ip": "10.0.0.206",  # (str) node ip
      "node": "west.worker.com",  # (str) node hostname
      "pod_ip": "10.244.1.75",  # (str) pod ip
      # (list) pod conditions
      "conditions": [
        {
          "condition": "ContainersReady",  # (str)
          "status": "True",  # (str)
          "message": "",  # (str)
          # (str) 업데이트 시간(yyyy-MM-dd HH:mm:SS)
          "updated": "2021-05-26 23:53:56",
        },
      ],
      # (list) docker image list
      "images": ["nginx:latest", "ubuntu:18.04"],
      "stime": "2021-05-26 23:53:56",  # (str) pod 시작 시간
    },
  ],
  "error": "no_error"  # (str) 에러 텍스트
}

pod_delete = {
  "name": "etri-west-cls",  # (str) 요청 pod가 상주하는 클러스터 이름
  "id": "123e4567-e89b...",  # (str) 등록된 클러스터에 부여한 uuid
  "error": "no_error"  # (str) 에러 텍스트
}

pod_migration_info = {
  "name": "etri-west-cls",  # (str) 요청 pod가 상주하는 클러스터 이름
  "id": "123e4567-e89b...",  # (str) 등록된 클러스터에 부여한 uuid
  "clusters": [
    {
      "name": "etri-west-cls",  # (str) 클러스터 이름
      "id": "123e4567-e89b...",  # (str) 클러스터 uuid
      "nodes": ["west.master", "west.worker1"]  # (str) 노드 목록
    },
    {
      "name": "etri-east-cls",  # (str) 클러스터 이름
      "id": "122ae4567-e89b...",  # (str) 클러스터 uuid
      "nodes": ["east.master", "east.worker1"]  # (str) 노드 목록
    }
  ],
  "error": "no_error"  # (str) 에러 텍스트
}

pod_migrate = {
  "name": "etri-west-cls",  # (str) 마이그레이션 대상 클러스터 이름
  "id": "123e4567-e89b...",  # (str) 등록된 클러스터에 부여한 uuid
  "pod": "http-vlc",  # (str) 마이그레이션 대상 pod 이름
  "target": {
    "cluster": "etri-west-cls",  # (str) 클러스터 이름
    "id": "123e4567-e89b...",  # (str) 클러스터 uuid
    "node": "west.master"  # (str) 노드 목록
  },
  "stime": "2021-05-26 23:53:56",  # (str) migrate 실행 시작 시간
  "error": "no_error"  # (str) 에러 텍스트
}
