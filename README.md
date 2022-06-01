# CloudWatchUpdateDashboard

CloudWatch 대시보드를 사용하다보면 업데이트를 해야하는 일이 많이 생긴다.  <br>
AutoScaling Group의 EC2 지표를 대시보드에서 확인하려면 미리 넣어줘야하며 많은 위젯을 사용한다면 그 일은 번거로워 지게 된다. <br>
Lambda를 사용하여 CloudWatch 대시보드에 Scale-Out 된 EC2의 지표를 자동으로 넣어주고, 다른 지표들까지 현재의 값으로 업데이트 해준다. <br>


![image](https://user-images.githubusercontent.com/43159901/171341416-d5c734e3-a5cc-4631-9459-20d129339d80.png)


## Agenda

### 1. Lambda에서 사용하기 위한 iam Role 생성 
![image](https://user-images.githubusercontent.com/43159901/171341773-d09dc4ba-4967-4f12-8142-215fe8ba8e1a.png)
![image](https://user-images.githubusercontent.com/43159901/171341857-80bba59f-e61d-46e1-a657-98b1dc399115.png)

#### 리소스의 정보를 읽기 위한 ReadOnlyAccess 권한, CloudWatch 권한 필요


### 2. Lambda 생성
![image](https://user-images.githubusercontent.com/43159901/171344485-5a079f10-be56-460e-a380-6e4a62390c5a.png)
![image](https://user-images.githubusercontent.com/43159901/171342295-a29e0415-f90c-47d6-b739-4389ba337bf3.png)
![image](https://user-images.githubusercontent.com/43159901/171342454-d3dc8021-199b-4380-b89b-e650cd5924c6.png)
#### Lambda 제한 시간 및 환경 변수 설정
![image](https://user-images.githubusercontent.com/43159901/171342599-73d8c24a-e974-466d-83c2-3eb28488f8fe.png)
#### lambda.py의 코드 기입 후 Deploy

### 3. Lambda 트리거 생성
![image](https://user-images.githubusercontent.com/43159901/171342786-0e931228-4d22-421d-8e7b-e37874a85efd.png)
![image](https://user-images.githubusercontent.com/43159901/171344149-6ba0e07e-0019-4284-a9b0-9f87198ce04a.png)
#### AutoScalingGroup에 의해 Scale-Out/In되는 이벤트 패턴

![image](https://user-images.githubusercontent.com/43159901/171344264-ec69334d-8718-42c8-99c7-208f9f667bc5.png)

![image](https://user-images.githubusercontent.com/43159901/171344569-230c26f5-ffb3-4748-b21a-b330f7522c32.png)
#### Lambda 트리거 확인


#### 
