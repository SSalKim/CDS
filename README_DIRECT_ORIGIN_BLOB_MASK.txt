CDS v3.1 direct-origin + blob-mask build

적용 목적
- Cloudflare Worker 프록시 경유를 제거하고 원본 이미지 URL을 직접 로드합니다.
- 표시 속도와 안정성을 원래 direct-origin 방식에 가깝게 회복합니다.
- 이미지가 로드된 뒤 가능한 경우 img.src를 blob: URL로 교체해 DOM에서 보이는 원본 URL을 줄입니다.

중요한 한계
- 브라우저 Network 탭에는 원본 data.kma.go.kr 요청이 보입니다.
- 원본 서버가 CORS를 허용하지 않으면 blob 변환은 실패하며, 이 경우 이미지는 direct URL 상태로 유지됩니다.
- 즉, 이 버전은 보안용 완전 은닉이 아니라 겉보기 URL 마스킹 + 속도/안정성 우선 버전입니다.

커밋 방법
1. 이 ZIP 안의 파일을 기존 GitHub Pages 프로젝트 폴더에 덮어씁니다.
2. private-worker, proxy-config.js 등 Worker 관련 파일은 더 이상 필요하지 않습니다.
3. PowerShell에서:

   cd "C:\Users\Administrator\Desktop\CDS_v3.1"
   git status
   git add .
   git commit -m "Rollback to direct origin blob mask"
   git push

문제 발생 시 확인
- index.html이 app.js를 마지막에 불러오는지 확인하세요.
- 파일명이 app(34).js가 아니라 app.js인지 확인하세요.
- GitHub Pages에서 Ctrl+F5로 강력 새로고침하세요.
