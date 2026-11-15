# 공개 모델 일기도 자동화 설정

## 확정 구성

- AIFS / GFS / AIGFS: 00, 06, 12, 18 UTC, 최근 9 cycle.
- CMC GDPS: 00, 12 UTC, 최근 5 cycle.
- 산출물: 계절별 gph200 또는 gph300, gph500, gph700, ept850, ept925, surfce/acptot, acrain, wnd850, wnd925.
- 아시아는 연중 surfce, acrain은 한반도만. 겨울철 한반도는 기존 3패널과 세로 비교본을 유지한다. AIGFS는 강수 첫 패널만 사용한다.
- +000h: surfce/acptot도 다른 시간대와 같은 제목에 `[000-000]`을 사용하고 누적량 채색은 비운다. 겨울철 한반도 acptot는 순간 고도·기온·바람·습구온도와 함께 3패널/세로 비교본을 모두 제공한다. 누적강수·강설 자료는 조회하지 않으며 acrain은 +000h에 생성하지 않는다.
- 빠른 무손실 WebP(`lossless=True, quality=80, method=4`). 지도는 한 번만 렌더링하고 최종 프레임에서 저장한다.
- 한반도 단일 패널은 오른쪽 6px, 위 2px, 아래 3px의 빈 여백을 줄인 634x725px이다. 지도·제목·컬러바 배치도 KIM 원본 패널에 가깝게 조정한다. 겨울철 3패널은 합성 후 가로 1750x660px / 세로 600x2000px로 맞춘다. 모델명은 KIM과 같은 `#0000ff`를 사용한다.
- 노트북이 online/idle이고 `linux`, `cds-vtg` 라벨이 있을 때 우선 사용한다. busy/offline/조회 실패는 ubuntu-24.04로 보낸다. 선택 직후 상태가 바뀌는 경합 가능성까지 완전히 없어지는 것은 아니다.
- AIGFS는 NOAA 공식 S3의 `aigfs.YYYYMMDD/HH/model/atmos/grib2/` 운영 파일을 우선 사용한다. 같은 버킷의 예전 GraphCastGFS 실험 경로와 혼합하지 않는다. S3 인덱스가 없을 때만 같은 cycle의 NOMADS 인덱스를 조회한다.
- 모델별 개수 제한과 이미지 12GB 상한을 함께 적용한다. 예측 내용에 따라 상한이 먼저 걸리면 오래된 cycle이 조기 정리될 수 있다. 최신 cycle 하나도 상한을 초과하면 삭제 대신 실패한다.

현재 최종 WebP 경로로 네 모델의 +000h 64장, +024h 74장을 로컬 실자료 검증했다. 이 표본을 전 시간표에 확대하면 +000h 포함 보관량은 약 9.72GB이다. 이는 전체 cycle 용량을 직접 측정한 확정치가 아니며, GitHub-hosted에서 전 구간 pilot과 실제 Drive URL 검증이 남아 있다.

## 새 Google Drive 계정 준비

**VTG의 Drive 계정, 폴더, 기존 GOOGLE_DRIVE_* Secrets는 사용하지 않는다.**

1. 새 Google 계정의 My Drive에 일기도 전용 폴더를 만든다. 폴더 자체를 공개하거나 다른 계정에 공유할 필요는 없다.
2. 폴더 URL의 `folders/` 다음 값을 폴더 ID로 확인한다.
3. [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트를 만들거나 선택하고 Google Drive API를 활성화한다.
4. Google Auth Platform의 OAuth 동의 화면을 설정한다. 외부 사용자 유형이면 테스트 사용자에 새 Drive 계정을 넣는다.
5. OAuth 클라이언트는 **데스크톱 앱**으로 만들고 클라이언트 JSON을 다운로드한다. JSON은 저장소 밖 Downloads 등에 둔다.
6. 아래 로컬 명령으로 브라우저에서 **새 계정**을 선택해 동의한다. 도구는 인증된 이메일과 폴더 소유자를 확인하고, 토큰을 화면이나 파일로 출력하지 않은 채 `gh secret set` 표준입력으로 등록한다.

외부 앱이 Testing 상태이면 Drive 권한을 받은 refresh token이 7일 후 만료될 수 있다. 장기 운영 전 앱 게시 상태/동의 화면 제한을 확인하고, 필요한 경우 In production으로 전환한 뒤 다시 인증해야 한다. 개인정보 처리방침/앱 검증 등의 요구는 프로젝트 설정과 이용 범위에 따라 별도 확인한다. [Google OAuth offline access](https://developers.google.com/identity/protocols/oauth2/web-server#offline), [토큰 만료 조건](https://developers.google.com/identity/protocols/oauth2#expiration).

Drive API 전체 권한을 요청하므로 동의 화면을 확인해야 한다. 코드의 자동 업로드/삭제는 예상 이메일이 소유한 전용 폴더의 namespace 태그 파일로 제한한다. VTG 계정으로 잘못 로그인하면 다른 계정으로 자동 전환하지 않고 실패한다.

## 로컬 인증 명령

PowerShell, 프로젝트 루트에서 실행한다. `<...>`는 본인 값으로 바꾼다. 키/토큰을 채팅이나 코드에 붙이지 않는다.

```powershell
gh auth status
& .\local_tools\weathermesh\.venv\Scripts\python.exe -m pip install -r requirements-public-charts-auth.txt
& .\local_tools\weathermesh\.venv\Scripts\python.exe public_charts_authorize.py `
  --client-secrets "$env:USERPROFILE\Downloads\<다운로드한 OAuth JSON 파일명>" `
  --folder-id "<전용 폴더 ID>" `
  --account-email "<새 Drive 계정 이메일>" `
  --register-repo "SSalKim/CDS"
```

`gh` 명령이 없다면 [GitHub CLI](https://cli.github.com/)를 설치하고 `gh auth login`으로 저장소에 접근 가능한 계정으로 로그인한다. Windows에서는 `winget install --id GitHub.cli` 후 터미널을 다시 여는 방법도 있다.

등록되는 새 repository Secrets는 다음 5개뿐이다.

```text
PUBLIC_CHARTS_DRIVE_CLIENT_ID
PUBLIC_CHARTS_DRIVE_CLIENT_SECRET
PUBLIC_CHARTS_DRIVE_REFRESH_TOKEN
PUBLIC_CHARTS_DRIVE_FOLDER_ID
PUBLIC_CHARTS_DRIVE_ACCOUNT_EMAIL
```

기존 VTG Secrets를 지우거나 덮어쓰지 않는다. 기존 OAuth 클라이언트 앱을 재사용하더라도 refresh token은 반드시 새 Drive 계정으로 동의받아야 한다.

## Actions 시험 순서

코드를 main에 반영한 뒤 Actions의 `Generate public model charts`를 수동 실행한다. 예약 작업은 repository variable `PUBLIC_CHARTS_ENABLED=true`가 없으면 실행하지 않는다.

1. `dry_run=true`, `runner_mode=github-hosted`로 계획만 확인한다. 인증·다운로드·업로드·삭제는 하지 않는다.
2. 로컬 인증 도구가 계정/폴더 검사를 통과한 뒤 Secrets를 등록했다고 표시되는지 확인한다. Actions Secrets는 로컬 명령에서 자동으로 읽을 수 없으며, 실제 workflow가 자체 계정 검사 단계를 다시 실행한다.
3. `dry_run=false`, 모델 하나, 원하는 cycle, `hours=0,24`, `max_leads=2`로 업로드·비로그인 이미지 URL·제목·시간대를 확인한다. **실제 모드는 만료 파일 영구 삭제까지 수행할 수 있으므로 전용 폴더만 사용한다.**
4. 한 모델 전 시간대, 그다음 네 모델로 확장하여 GitHub-hosted에서 실행시간·디스크·메모리·이미지 bytes를 계측한다.
5. 검증 후 repository variable `PUBLIC_CHARTS_ENABLED`를 `true`로 설정한다. 10분마다 최근 미완성 cycle을 확인한다.

`PUBLIC_CHARTS_START_CYCLE=2026111512`는 운영 시작 초기시각의 하한이다. 이후 자동 실행은 이 시각 이전을 조회하지 않고, 보관 개수 범위 안의 누락 cycle도 다시 확인한다. 예측시간별로 초기시각을 교차 처리해 최신 cycle 하나가 끝날 때까지 이전 미완성 cycle이 완전히 밀리지 않도록 한다. 수동 실행에서 하한보다 오래된 cycle을 지정하면 다운로드 전에 거부한다.

공개/비공개 목록의 각 행에는 `render_version`을 기록한다. 이전 규격의 이미지는 새 규격으로 다시 생산하기 전까지 그대로 제공하며, 현재 버전의 이미지로 교체된 뒤에만 기존 파일을 정리한다.

기존 `RUNNER_STATUS_TOKEN`은 GitHub 러너 조회 용도로만 재사용한다. 이것이 없어 조회에 실패해도 GitHub-hosted로 진행한다.

## 저장/삭제 흐름

원시 GRIB와 기본 입력은 러너의 전용 임시 경로에서만 사용한다. 완료한 lead 뒤에 정리하고, 다음 계산에 필요한 압축된 누적 체크포인트만 Actions cache에 남긴다. 캐시는 없어질 수 있으므로 원본 재수집으로 복구한다. **원시자료 24시간 보관을 보장하는 구조는 아니다.**

계정 검증 -> 준비된 고도/바람 먼저 생산 -> 강수/겨울 입력 확인 -> WebP 업로드 -> 서버 MD5/size/공개 권한 확인 -> 새 cycle 첫 파일 비로그인 URL 확인 -> URL manifest 반영 -> Git push 확인 -> 오래된 관리 이미지 영구 삭제 순서다.

공개 manifest는 `data/public_charts_manifest.json`이다. 인증/계정 이메일/토큰/삭제 상태는 넣지 않는다. CDS는 raw GitHub의 최신 manifest를 조회하므로 이미지 갱신마다 Pages를 재배포할 필요가 없다. 별도 Drive 계정의 private `state.json`, `manifest.json`은 관리 태그를 가진 파일이며 일반 공개하지 않는다.

삭제는 파일 ID마다 실제 부모 폴더·소유자·namespace·ETag를 다시 확인한다. 다른 계정, VTG 파일, 폴더 자체, 사용자 개인 파일은 대상이 아니다. manifest 커밋이 실패하면 원격 이미지를 삭제하지 않는다. 공개 목록 캐시를 고려해 새 목록 게시 확인 후 10분이 지난 파일만 삭제하므로, 그동안 만료 파일이 잠시 추가 보관될 수 있다. 이 유예 파일까지 이미지 12GB 예산에 포함한다. 상한 때문에 업로드가 멈추면 먼저 검증된 보관 목록을 공개하고 정리를 끝낸 뒤 다음 실행에서 이어간다.

Drive v3가 메타데이터 ETag를 생략하면 v2에서 소유자·폴더·비공개 관리 태그와 ETag를 함께 다시 조회하고, 해당 v2 리소스에 `If-Match` 조건부 갱신/삭제를 수행한다. 양쪽 모두 ETag가 없으면 변경을 거부한다. 관리 JSON의 v2 갱신은 `newRevision=false`로 이전 리비전 누적을 방지한다.

만료 이미지 삭제는 실행당 최대 300개로 나누어 수행한다. 한 번에 삭제가 끝나지 않아도 다음 실행에서 이어가며, 최신 자료가 삭제 대상으로 바뀌지는 않는다.

## 로컬 그림 확인

아래는 Drive와 연결하지 않는 로컬 모드다. 기존 캐시는 검증해 재사용하며 지우지 않는다. 추가 필드와 체크포인트를 같은 캐시 경로에 기록할 수 있고, 캐시에 없는 필드는 공개 소스에서 받을 수 있다.

```powershell
$env:PUBLIC_CHARTS_MAP_DIR = (Resolve-Path .\local_tools\weathermesh\maps).Path
& .\local_tools\weathermesh\.venv\Scripts\python.exe public_charts_run.py --local `
  --models aifs --cycle 2026111500 --hours 24 --max-leads 1 `
  --cache-root outputs/open-models-20261115 --workdir outputs/public-charts-preview
```

현재 폰트/컬러/도법/컨투어는 로컬 최종 검토본에서 분리했다. 한국 시도 경계는 기존 MAP에서 가져온 동일 스냅샷이며, public 배포 전 해당 자료의 재배포/출처 표기 조건도 확인해야 한다.
