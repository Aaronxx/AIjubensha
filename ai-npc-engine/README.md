启动方式

  玩家端后端（game-server）：

  cd D:/workspace/AIjubensha/game-server
  uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

  访问：
  - API 文档：http://localhost:8000/docs
  - 房间列表：http://localhost:8000/api/rooms

  后台管理系统（admin-server）：

  cd D:/workspace/AIjubensha/admin-server
  uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload

  访问：
  - 后台 API 文档：http://localhost:8001/docs
  - 仪表盘：http://localhost:8001/api/admin/dashboard