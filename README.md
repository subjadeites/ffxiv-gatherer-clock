# FFXIV-Gatherer-Clock

基于Python3.12.2的本地时限采集时钟  
基于`WxPython`构建GUI，代码理论兼容Python3.11.x  
基于GPL v3协议开源  

### 依赖与封装
构建：`requirements_release.txt`  
开发：`requirements.txt`  
  
封装：`auto-py-to-exe`(`pyinstaller==5.13.2`)，使用`upx==4.2.4`压缩

### 目前已实现功能</br>

✓ 精确的ET时钟用于触发闹钟  
✓ GUI界面  
✓ 6.x所有时限材料覆盖，可以选择等级  
✓ 2.0-5.x旧版本时限支持  
✓ 对不同时限种类进行基本筛选  
✓ 采掘/园艺/all三种职业选择  
✓ 有GUI界面下开放更加自由的选择  
✓ 离线地图支持
✓ 可自由选择是否开启详情播报的TTS  
✓ 在线数据源支持(用于更新数据源时不用重新下载数据源)  

### 计划中功能

X ACT触发器支持(用于直接显示在游戏界面里)  
X 采集笔记功能（光武成就）

### NGA内发布地址

https://bbs.nga.cn/read.php?tid=29755989  
有什么好的建议以及出现bug了请回复告知/github提交issure  
