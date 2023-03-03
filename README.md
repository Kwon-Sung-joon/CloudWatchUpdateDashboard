# CloudWatchUpdateDashboard
- AutoScaling에 따른 CloudWatch 대시보드 업데이트 자동화

# Architecture
![image](https://user-images.githubusercontent.com/43159901/171341416-d5c734e3-a5cc-4631-9459-20d129339d80.png)

# Widgets
* EC2 - CPUtilization/NetworkIn/NetworkOut/EBSReadOps/EBSWriteOps/Memory (CloudWatchAgent 사용 필요)
* VPN - TunnelDataOut/TunnelDataIn
* RDS - CPUtilization/FreeStorageSpace/DatabaseConnections/DBLoad
* ElastiCache - CurrConnections/SwapUsage/NetworkBytesIn/NetworkBytesOut
* ALB - UnhealthyHost/HTTPCode_Target_2XX_Count/HTTPCode_Target_5XX_Count/RequestCount/TargetResponseTime
* EFS - PercentIOLimit

