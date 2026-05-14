# CDS v3.0 Worker Proxy 리팩토링 적용 안내

이 통합본은 원본 이미지 URL 패턴을 public GitHub Pages 쪽 JS에서 제거하고, Cloudflare Worker 내부로 옮긴 버전입니다.

## 파일 구조

```text
index.html
style.css
models.js                  # public: folder 제거, 모델 시간/기간 메타만 유지
products.js                # public: 실제 파일명 제거, 지원 모델/이미지 개수만 유지
hazards.js
ensemble.js
analysis.js
edit.js
catalog-config.js
aux-data.js
aux-rules.js
proxy-config.js            # public: Worker URL 설정
app.js                     # public: Worker /chart URL만 호출
private-worker/
  cds-worker.js            # private: 실제 원본 folder/pattern mapping 포함
private-worker-wrangler.toml
```

## 매우 중요

`private-worker/cds-worker.js`에는 실제 원본 파일명과 folder mapping이 들어 있습니다. 원본 URL 패턴을 숨기려면 이 파일을 public GitHub 저장소에 올리면 안 됩니다.

`.gitignore`에 이미 `private-worker/`가 들어 있으므로 VS Code/Git으로 push하면 기본적으로 제외됩니다. 단, GitHub 웹 업로드로 직접 드래그하면 `.gitignore`가 막아주지 않으니 직접 올리지 마세요.

## 1. Cloudflare Worker 만들기 - 웹 대시보드 방식

1. Cloudflare 로그인
2. Workers & Pages로 이동
3. Create application 또는 Create Worker 선택
4. 빈 Worker를 만든 뒤 코드 편집 화면으로 이동
5. `private-worker/cds-worker.js` 내용을 전체 복사해서 붙여넣기
6. Deploy 클릭
7. 배포 후 Worker URL 복사
   - 예: `https://cds-chart-proxy.your-name.workers.dev`

확인:

```text
https://cds-chart-proxy.your-name.workers.dev/health
```

화면에 `ok`가 나오면 Worker가 살아 있습니다.

## 2. proxy-config.js 수정

GitHub Pages에 올라갈 `proxy-config.js`에서 아래 값을 실제 Worker URL로 바꾸세요.

```javascript
window.CDS_PROXY_BASE_URL="https://cds-chart-proxy.your-name.workers.dev";
```

주의: 끝에 `/`는 붙이지 않아도 됩니다.

## 3. GitHub Pages에 올릴 파일

public GitHub Pages 저장소에는 아래 파일만 올리면 됩니다.

```text
index.html
style.css
models.js
products.js
hazards.js
ensemble.js
analysis.js
edit.js
catalog-config.js
aux-data.js
aux-rules.js
proxy-config.js
app.js
.gitignore
README_WORKER_SETUP.md
```

올리면 안 되는 파일:

```text
private-worker/cds-worker.js
private-worker-wrangler.toml
*.original.js
extracted.json
extract.js
```

## 4. 선택 설정: Worker 접근 제한

Worker Settings에서 Environment variables를 추가할 수 있습니다.

권장 변수:

```text
ALLOWED_ORIGINS=https://깃허브아이디.github.io
CACHE_TTL=3600
```

`ALLOWED_ORIGINS`를 비워두면 모든 곳에서 Worker URL 호출이 가능합니다. 원본 URL 패턴은 여전히 숨겨지지만, Worker URL 자체는 누구나 호출할 수 있습니다.

더 제한하고 싶으면 `ALLOWED_ORIGINS`에 GitHub Pages origin을 넣으세요.

예:

```text
https://kwj1407.github.io
```

## 5. 작동 방식

브라우저에서는 이제 이런 Worker URL만 보입니다.

```text
https://...workers.dev/chart?menu=forecast&category=asia&product=gph500&model=kim_gdps&run=2026050800&fh=000&index=0
```

실제 원본 URL은 Worker 내부에서만 조립됩니다.

## 6. 문제 해결

### 화면에 Worker 주소 미설정 메시지가 뜸

`proxy-config.js`의 `CDS_PROXY_BASE_URL`이 아직 placeholder입니다.

### 이미지가 모두 자료 없음으로 뜸

1. Worker `/health` 확인
2. `proxy-config.js` 주소 확인
3. Cloudflare Worker 로그 확인
4. `ALLOWED_ORIGINS`를 잠시 비워두고 테스트
5. 브라우저에서 Ctrl+F5 강력 새로고침

### GitHub에 올렸는데 원본 패턴이 보임

public 저장소에 `private-worker/cds-worker.js`를 올린 것입니다. 즉시 삭제하고 commit/push하세요.

