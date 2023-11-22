cluster_list = {
  "clusters": [
    {
      "id": "123e4567-e89b",  # (str) 등록된 클러스터에 부여한 uuid
      "name": "etri-west-cluster",  # (str) 등록된 클러스터 이름
      "desc": "cluster is ...",  # (str) 등록된 클러스터의 설명
      "state": "Active",  # (str) 등록된 클러스터의 상태("Active" 혹은 "Pending" 혹은 "Unavailable")
      "api_address": "10.0.0.206:443",  # (str) 클러스터 kube-api-server 주소
      "api_version": "1.21.14",  # (str) 등록된 클러스터의 상태
      "registration": "sudo docker run –d –privileged –restart=unless-stopped –net=host –v /etc/kubernetes:/etc/kubernetes –v krunivs/cedge-agent:1.0 –station http://10.0.0.220 –token asldkhlkhaasdlklkha",
      # (str) 클러스터 등록 명령어
      "nodes": 2,  # 클러스터에 등록된 노드 수
      "mc_network": {
        "connect_id": "123e451-e834-1242",
        # (str) MC network status("connected“ 혹은 ”unavailable”)
        "status": "connected",
        # (str) global vpn 설치 여부(“enabled” 혹은 “disabled”)
        "globalnet": "enabled",
        # (str) global vpn 서브넷 범위("244.0.0.0/8")
        "global_cidr": "244.0.0.0/8",
        # (str) tunneling driver(“wireguard” 혹은 “libswan” 혹은 “ipsec”)
        "cable_driver": "wireguard",
        # (str) public ip("211.237.16.76")
        # (str) cluster name
        "broker_role": "Local",
        "local": {
          "name": "etri-west-cls",
          "public": "211.237.16.76",
          # (str) gateway ip("10.0.0.206")
          "gateway": "10.0.0.206",
          # (str) service network("10.55.0.0/16")
          "service_cidr": "10.55.0.0/16",
          # (str) pod network("10.244.0.0/16")
          "cluster_cidr": "10.244.0.0/16"
        },
        "remote": {
          "name": "etri-west-cls",
          "public": "211.237.17.76",
          # (str) gateway ip("10.0.0.208")
          "gateway": "10.0.0.207",
          # (str) service network("10.55.0.0/16")
          "service_cidr": "10.54.0.0/16",
          # (str) pod network("10.244.0.0/16")
          "cluster_cidr": "10.245.0.0/16"
        },
      },
      "conditions": [
        {
          "condition": "ContainersReady",  # (str)
          "status": "True",  # (str)
          "message": "",  # (str)
          # (str) 업데이트 시간(yyyy-MM-dd HH:mm:SS)
          "updated": "2021-05-26 23:53:56",
        },
      ]
    },
    {
      "id": "123e4567-c02a",  # (str) 등록된 클러스터에 부여한 uuid
      "name": "etri-north-cluster",  # (str) 등록된 클러스터 이름
      "desc": "cluster is ...",  # (str) 등록된 클러스터의 설명
      "state": "Pending",  # (str) 등록된 클러스터의 상태("Active" 혹은 "Pending" 혹은 "Unavailable")
      "api_address": "10.0.0.207:443",  # (str) 클러스터 kube-api-server 주소
      "api_version": "1.21.12",  # (str) 등록된 클러스터의 상태
      "registration": "sudo docker run -d -privile...",  # (str) 클러스터 등록 명령어
      "nodes": 2,  # 클러스터에 등록된 노드 수
      "mc_network": {
        "connect_id": "123e451-e834-1231",
        # (str) MC network status("connected“ 혹은 ”unavailable”)
        "status": "connected",
        # (str) global vpn 설치 여부(“enabled” 혹은 “disabled”)
        "globalnet": "enabled",
        # (str) global vpn 서브넷 범위("244.0.0.0/8")
        "global_cidr": "244.0.0.0/8",
        # (str) tunneling driver(“wireguard” 혹은 “libswan” 혹은 “ipsec”)
        "cable_driver": "wireguard",
        # (str) public ip("211.237.16.76")
        # (str) cluster name
        "broker_role": "Remote",
        "local": {
          "name": "etri-west-cls",
          "public": "211.237.16.76",
          # (str) gateway ip("10.0.0.206")
          "gateway": "10.0.0.206",
          # (str) service network("10.55.0.0/16")
          "service_cidr": "10.55.0.0/16",
          # (str) pod network("10.244.0.0/16")
          "cluster_cidr": "10.244.0.0/16"
        },
        "remote": {
          "name": "etri-north-cls",
          "public": "211.237.16.77",
          # (str) gateway ip("10.0.0.208")
          "gateway": "10.0.0.208",
          # (str) service network("10.55.0.0/16")
          "service_cidr": "10.55.0.0/16",
          # (str) pod network("10.244.0.0/16")
          "cluster_cidr": "10.244.0.0/16"
        },
      },
      "conditions": [
        {
          "condition": "ContainersReady",  # (str)
          "status": "True",  # (str)
          "message": "etri-north-cluster",  # (str)
          # (str) 업데이트 시간(yyyy-MM-dd HH:mm:SS)
          "updated": "2021-05-26 23:53:56",
        },
      ]
    },
  ],
  "error": "no_error"  # (str) 에러 텍스트
}

cluster_details = {
  "clusters": [
    {
      "id": "123e4567-e89b...",  # (str) 등록된 클러스터에 부여한 uuid
      "name": "etri-west-cluster",  # (str) 등록된 클러스터 이름
      "desc": "cluster is ...",  # (str) 등록된 클러스터의 설명
      # (str) 등록된 클러스터의 상태("Active" 혹은 "Pending" 혹은 "Unavailable")
      "state": "Active",
      "api_address": "10.0.0.206:443",  # (str) 클러스터 kube-api-server 주소
      "api_version": "1.21.14",  # (str) 등록된 클러스터의 상태
      "registration": "sudo docker run -d -privile...",  # (str) 클러스터 등록 명령어
      "nodes": 2,  # 클러스터에 등록된 노드 수
      "mc_network": {
        "connect_id": "123e451-e834-1231",
        # (str) MC network status("connected“ 혹은 ”unavailable”)
        "status": "connected",
        # (str) global vpn 설치 여부(“enabled” 혹은 “disabled”)
        "globalnet": "enabled",
        # (str) global vpn 서브넷 범위("244.0.0.0/8")
        "global_cidr": "244.0.0.0/8",
        # (str) tunneling driver(“wireguard” 혹은 “libswan” 혹은 “ipsec”)
        "cable_driver": "wireguard",
        # (str) public ip("211.237.16.76")
        # (str) cluster name
        "local": {
          "name": "etri-west-cls",
          "public": "211.237.16.76",
          # (str) gateway ip("10.0.0.206")
          "gateway": "10.0.0.206",
          # (str) service network("10.55.0.0/16")
          "service_cidr": "10.55.0.0/16",
          # (str) pod network("10.244.0.0/16")
          "cluster_cidr": "10.244.0.0/16"
        },
        "remote": {
          "name": "etri-north-cls",
          "public": "211.237.16.76",
          # (str) gateway ip("10.0.0.208")
          "gateway": "10.0.0.208",
          # (str) service network("10.55.0.0/16")
          "service_cidr": "10.55.0.0/16",
          # (str) pod network("10.244.0.0/16")
          "cluster_cidr": "10.244.0.0/16"
        },
      },
      "conditions": [
        {
          "condition": "ContainersReady",  # (str)
          "status": "True",  # (str)
          "message": "",  # (str)
          # (str) 업데이트 시간(yyyy-MM-dd HH:mm:SS)
          "updated": "2021-05-26 23:53:56",
        },
      ]
    }
  ],
  "error": "no_error"  # (str) 에러 텍스트
}

node_list = {
  "name": "etri-west-cluster",  # (str) 조회 대상 클러스터 이름
  "id": "123e4567-e89b...",  # (str) 등록된 클러스터에 부여한 uuid
  "nodes": [
    {
      "name": "west.master",  # (str) 노드의 이름(hostname)
      "host_if": "eth0",  # (str) 노드의 호스트 인터페이스
      "ip": "10.0.0.206",  # (str) 노드의 IP 주소
      # (str) 노드의 상태("Pending" 혹은 "Running" 혹은 "Terminated")
      "state": "Running",
      "role": "Master",  # (str) "Worker" 혹은 ”Master"
      "k8s_version": "1.21.0",  # (str) kubernetes 설치 버전
      "os": "ubuntu20.04",  # (str) 노드에 설치된 OS
      "number_of_cpu": 4,  # (int) 최대 CPU 코어 수
      "ram_size": "8192KiB",  # (str) 설치된 메모리 용량
      "pods": {
        "max_pods": "22",  # (str) 최대 배포 가능한 pod 수
        "usage": "15.2",  # (str) 現 운영 pod 수(running pods/max pods*100;%)
      },
      # (str) node 부팅 시간(yyyy-MM-dd HH:mm:SS.f)
      "stime": "2022-11-29 14:01:56",
    },
    {
      "name": "west.worker",  # (str) 노드의 이름(hostname)
      "host_if": "eth0",  # (str) 노드의 호스트 인터페이스
      "ip": "10.0.0.207",  # (str) 노드의 IP 주소
      # (str) 노드의 상태("Pending" 혹은 "Running" 혹은 "Terminated")
      "state": "Running",
      "role": "Master",  # (str) "Worker" 혹은 ”Master"
      "k8s_version": "1.21.0",  # (str) kubernetes 설치 버전
      "os": "ubuntu20.04",  # (str) 노드에 설치된 OS
      "number_of_cpu": 4,  # (int) 최대 CPU 코어 수
      "ram_size": "8192KiB",  # (str) 설치된 메모리 용량
      "pods": {
        "max_pods": "22",  # (str) 최대 배포 가능한 pod 수
        "usage": "15.2",  # (str) 現 운영 pod 수(running pods/max pods*100;%)
      },
      # (str) node 부팅 시간(yyyy-MM-dd HH:mm:SS.f)
      "stime": "2022-11-29 14:01:56",
    },
  ],
  "error": "no_error"  # (str) 에러 텍스트
}

node_usage = {
  "name": "etri-west-cluster",  # (str) 조회 대상 클러스터 이름
  "id": "123e4567-e89b...",  # (str) 등록된 클러스터에 부여한 uuid
  "nodes": [
    {
      "name": "west.master",  # (str) 노드의 이름(hostname)
      "pods": {
        "max_pods": "22",  # (str) 최대 배포 가능한 pod 수
        "usage": "15.2",  # (str) 現 운영 pod 수(running pods/max pods*100;%)
      },
      "cpu_usages": [
        {
          "time": "2022-11-10 22:10:11.3",  # (str) yyyy-MM-dd HH:mm:SS.f
          "usage": 16.3,  # (float) 단위: %
          "total": "4",  # (str) 단위: 개
        },
      ],
      "mem_usages": [
        {
          "time": "2022-11-10 22:10:11.3",  # yyyy-MM-dd HH:mm:SS.f
          "usage": 6.3,  # (float) 단위: %
          "total": "8192KiB",  # (str) 설치된 메모리 용량
          "used": "516KiB"  # (str) 메모리 사용량
        },
      ],
      "net_usages": [
        {
          "time": "2022-11-10 22:10:05.3",  # %Y-%m-%d %H:%M:%S
          "rx_bytes": 12312312,  # (int) 단위: bytes
          "tx_bytes": 11312312,  # (int) 단위: bytes
        },
        {
          "time": "2022-11-10 22:10:06.3",  # %Y-%m-%d %H:%M:%S
          "rx_bytes": 14312312,  # (int) 단위: bytes
          "tx_bytes": 12312312,  # (int) 단위: bytes
        },
        {
          "time": "2022-11-10 22:10:07.3",  # %Y-%m-%d %H:%M:%S
          "rx_bytes": 13312312,  # (int) 단위: bytes
          "tx_bytes": 13312312,  # (int) 단위: bytes
        },
        {
          "time": "2022-11-10 22:10:08.3",  # %Y-%m-%d %H:%M:%S
          "rx_bytes": 13312312,  # (int) 단위: bytes
          "tx_bytes": 11312312,  # (int) 단위: bytes
        },
        {
          "time": "2022-11-10 22:10:09.3",  # %Y-%m-%d %H:%M:%S
          "rx_bytes": 11312312,  # (int) 단위: bytes
          "tx_bytes": 15312312,  # (int) 단위: bytes
        },
        {
          "time": "2022-11-10 22:10:10.3",  # %Y-%m-%d %H:%M:%S
          "rx_bytes": 17312312,  # (int) 단위: bytes
          "tx_bytes": 15312312,  # (int) 단위: bytes
        },
        {
          "time": "2022-11-10 22:10:11.3",  # %Y-%m-%d %H:%M:%S
          "rx_bytes": 15312312,  # (int) 단위: bytes
          "tx_bytes": 12312312,  # (int) 단위: bytes
        },
      ],
    },
  ],
  "error": "no_error"  # 에러 텍스트
}

mc_network_measure = {
  "measured": "true",  # (str) 네트워크 처리량 측정 완료 여부("true" 혹은 “false")
  "send": 901.0,  # (float) 단위: Mbps(Mega bit per seconds)
  "recv": 750.0,  # (float) 단위: Mbps(Mega bit per seconds)
  # (str) 네트워크 처리량 측정 시간
  # (str) throughput 측정 시간(yyyy-MM-dd HH:mm:SS.f)
  "throughput_measure_date": "2021-05-26 23:53:56.1",
  "error": "error text"  # (str) 에러 메시지
}

mc_network_latency = {
  "latency": 7.50,  # (float) 단위: ms(milli-seconds)
  # (str) latency 측정 시간(yyyy-MM-dd HH:mm:SS.f)
  "latency_measure_date": "2021-05-26 23:53:56.1",
  "error": "error text"  # (str) 에러 메시지
}
