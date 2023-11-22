service_list = {
  "name": "etri-west-cluster",  # (str) 조회 대상 클러스터 이름
  # (list) 조회 대상 클러스터와 연결된 클러스터 목록
  "id": "123e4567-e89b...",  # (str) 등록된 클러스터에 부여한 uuid
  "services": [
    {
      "name": "proxy-vlc-http",  # (str) service name
      # (str) service의 상태("Active" 혹은 "NotReady" 혹은 "Terminating")
      "state": "Active",
      "service_export": {
        "status": "true",  # (str) "true" 혹은 “false"
        "target": "etri-east-cls",  # (str) export된 cluster name
        "reason": "",  # (str) service export 실패 시 원인
        # (str) export target 클러스터에서 접근 대상 서비스의 접근 ip
        "clusterset_ip": "242.0.255.253",
        # (str) export target 클러스터에서 접근 대상 서비스의 접근 dns
        "service_discovery": "vlc-http.etri.svc.clusterset.local",
        "stime": "2021-05-26 23:53:56",  # (str) export된 시간
      },
      # (str) namespace name
      "namespace": "etri",
      # (str) service 타입(“ClusterIP" 혹은 "NodePort" 혹은 "LoadBalancer" 혹은 "ExternalName")
      "service_type": "ClusterIP",
      # (str) service의 cluster ip
      "cluster_ip": "10.55.8.65",
      # (str) service의 external ip
      "external_ips": [],
      "ports": [
        {
          "name": "http",  # (str) port 이름
          "port": "8080",  # (str) service port 이름
          "node_port": "31001",  # (str) node port
          "target_port": "80",  # (str) container port
          "protocol": "TCP",  # (str) TCP 혹은 UDP
        },
        {
          "name": "http-internal",  # (str) port 이름
          "port": "443",  # (str) service port 이름
          "node_port": "",  # (str) node port
          "target_port": "444",  # (str) container port
          "protocol": "TCP",  # (str) TCP 혹은 UDP
        },
      ],
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
      "stime": "2021-10-26 23:53:56",  # (str) service 실행 시간
    },
    {
      "name": "proxy-vlc-http2",  # (str) service name
      # (str) service의 상태("Active" 혹은 "NotReady" 혹은 "Terminating")
      "state": "unavailable",
      "service_export": {
        "status": "false",  # (str) "true" 혹은 “false"
        "target": "etri-east-cls",  # (str) export된 cluster name
        "reason": "",  # (str) service export 실패 시 원인
        # (str) export target 클러스터에서 접근 대상 서비스의 접근 ip
        "clusterset_ip": "242.0.255.253",
        # (str) export target 클러스터에서 접근 대상 서비스의 접근 dns
        "service_discovery": "vlc-http.etri.svc.clusterset.local",
        "stime": "2021-05-26 23:53:56",  # (str) export된 시간
      },
      # (str) namespace name
      "namespace": "etri-test",
      # (str) service 타입(“ClusterIP" 혹은 "NodePort" 혹은 "LoadBalancer" 혹은 "ExternalName")
      "service_type": "ClusterIP v2",
      # (str) service의 cluster ip
      "cluster_ip": "10.55.8.67",
      # (str) service의 external ip
      "external_ips": [],
      "ports": [
        {
          "name": "http-internal",  # (str) port 이름
          "port": "8080",  # (str) service port 이름
          "node_port": "30800",  # (str) node port
          "target_port": "80",  # (str) container port
          "protocol": "TCP",  # (str) TCP 혹은 UDP
        },
      ],
      "selector": ["app:proxy-vlc-http, app:proxy-vlc-http2"],
      "conditions": [
        {
          "condition": "ContainersReady",  # (str)
          "status": "True",  # (str)
          "message": "test message",  # (str)
          # (str) 업데이트 시간(yyyy-MM-dd HH:mm:SS)
          "updated": "2021-05-26 23:53:56",
        },
      ],
      "stime": "2021-05-26 23:53:56",  # (str) service 실행 시간
    },
  ],
  "error": "no_error"  # (str) 에러 텍스트
}

service_delete = {
  "name": "etri-west-cls",  # (str) 클러스터 이름
  "id": "123e4567-e89b...",  # (str) 클러스터 uuid
  "service": "http-vlc",  # (str) 삭제 service name
  "error": "no_error"  # (str) 에러 텍스트
}

service_export = {
  "name": "etri-west-cls",  # (str) 클러스터 이름
  "id": "123e4567-e89b...",  # (str) 클러스터 uuid
  "service": "http-vlc",  # (str) export service name
  "error": "no_error"  # (str) 에러 텍스트
}
