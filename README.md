# AIjubensha

鍩轰簬澶ц瑷€妯″瀷鐨勫浜哄湪绾?AI 鍓ф湰鏉€锛圡urder Mystery Game锛夊钩鍙帮細鐢?AI 鎵紨鍓ф湰涓殑 NPC 瑙掕壊锛岀帺瀹跺湪鎴块棿鍐呰仈鏈鸿繘琛屽墽鎯呭璇濄€佹悳璇併€佹姇绁ㄤ笌缁撶畻銆?
## 鍔熻兘鐗规€?
- 馃幁 **AI NPC 寮曟搸**锛歀LM 椹卞姩鐨?NPC 瑙掕壊鎵紨锛屾敮鎸佷富/澶囨ā鍨嬭嚜鍔ㄥ垏鎹€侀噸璇曚笌瓒呮椂鎺у埗锛屽唴缃墽鏈牎楠屼笌 NPC 鐘舵€佺鐞?- 馃彔 **鎴块棿绯荤粺**锛氬垱寤?鍔犲叆鎴块棿锛學ebSocket 瀹炴椂鑱旀満
- 馃摐 **鍓ф湰绠＄悊**锛氬墽鏈€佽鑹层€佸墽鎯呮帹杩涳紙dialogue / investigation / voting / settlement锛?- 馃攼 **鐢ㄦ埛绯荤粺**锛欽WT 璁よ瘉锛堟敞鍐?鐧诲綍锛?- 馃洅 **鍟嗗簵绯荤粺**锛氭父鎴忓唴閬撳叿/瑙掕壊鍟嗗簵
- 馃洜 **绠＄悊鍚庡彴**锛氱嫭绔嬪悗鍙版湇鍔★紝鎻愪緵浠〃鐩樸€佸墽鏈笌瑙掕壊绠＄悊鎺ュ彛

## 椤圭洰缁撴瀯

```
AIjubensha/
鈹溾攢鈹€ game-server/       # 鐜╁绔悗绔紙FastAPI + WebSocket + PostgreSQL + Redis锛?鈹溾攢鈹€ admin-server/      # 绠＄悊鍚庡彴鏈嶅姟锛團astAPI锛岀嫭绔嬬鍙ｏ級
鈹溾攢鈹€ ai-npc-engine/     # AI NPC 寮曟搸锛圠LM 瀹㈡埛绔€丯PC 宸ュ巶銆佸墽鏈牎楠岋級
鈹溾攢鈹€ flutter-client/    # Flutter 璺ㄥ钩鍙板鎴风锛圓ndroid / iOS / 妗岄潰 / Web锛?鈹溾攢鈹€ ios-client/        # 鍘熺敓 iOS 瀹㈡埛绔紙Xcode 宸ョ▼锛?鈹溾攢鈹€ web-app/           # Web 椤甸潰鍘熷瀷
鈹溾攢鈹€ docker-compose.yml # 鏈湴鍩虹璁炬柦锛圥ostgreSQL 16 + Redis 7 + game-server锛?鈹斺攢鈹€ codemagic.yaml     # iOS 鏋勫缓娴佹按绾匡紙Codemagic CI锛?```

## 鎶€鏈爤

| 灞?| 鎶€鏈?|
|---|---|
| 鍚庣 | Python 路 FastAPI 路 SQLAlchemy 2 (asyncpg) 路 WebSockets |
| 鏁版嵁 | PostgreSQL 16 路 Redis 7 |
| 璁よ瘉 | JWT锛坧ython-jose + passlib锛?|
| AI | DeepSeek API锛坄deepseek-chat`锛屾敮鎸佽嚜瀹氫箟 fallback 妯″瀷锛?|
| 瀹㈡埛绔?| Flutter锛坧rovider 鐘舵€佺鐞嗭級路 Swift / Xcode |
| 鍩虹璁炬柦 | Docker Compose 路 Codemagic CI |

## 蹇€熷紑濮?
### 鍓嶇疆瑕佹眰

- Python 3.10+
- Docker & Docker Compose锛堟垨鑷 PostgreSQL / Redis锛?- Flutter SDK锛堣繍琛屽鎴风锛?- [DeepSeek API Key](https://platform.deepseek.com/)

### 1. 鍚姩鍩虹璁炬柦

```bash
docker compose up -d postgres redis
```

### 2. 閰嶇疆鐜鍙橀噺

```bash
cp game-server/.env.example game-server/.env
# 缂栬緫 .env锛屽～鍏?DEEPSEEK_API_KEY
```

### 3. 鍚姩鐜╁绔悗绔紙绔彛 8000锛?
```bash
cd game-server
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
# API 鏂囨。锛歨ttp://localhost:8000/docs
```

### 4. 鍚姩绠＄悊鍚庡彴锛堢鍙?8001锛?
```bash
cd admin-server
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
# 鍚庡彴 API 鏂囨。锛歨ttp://localhost:8001/docs
```

### 5. 杩愯 Flutter 瀹㈡埛绔?
```bash
cd flutter-client
flutter pub get
flutter run
```

涔熷彲浠ョ敤 Docker Compose 涓€閿惎鍔ㄥ畬鏁村悗绔細

```bash
cp .env.example .env   # 濉叆 DEEPSEEK_API_KEY
docker compose up --build
```

## 寮€鍙?
```bash
cd game-server
pip install -r requirements.txt
pytest
```

## License

This project is licensed under the [PolyForm Noncommercial License 1.0.0](LICENSE).

Required Notice: Copyright (c) 2026 Aaronxx

Personal study, research, hobby, and other noncommercial use is permitted. **Commercial use requires a separate license from the author.**