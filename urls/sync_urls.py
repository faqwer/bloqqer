import os
import re

def get_pure_url(line):
    """
    어떤 형태의 줄(주석, 공백 포함)에서도 순수 URL 본체만 추출하여 표준화합니다.
    """
    # 1. HTML 주석 기호 제거
    clean = line.replace('', '').strip()
    
    # 2. 정규표현식으로 http로 시작하는 URL 본체만 추출
    # (공백, 주석기호, 따옴표 등을 제외한 실제 주소만 타겟팅)
    match = re.search(r'(https?://[^\s<>"]+)', clean)
    if match:
        # 소문자 변환 및 끝 슬래시 제거하여 비교 데이터 통일
        return match.group(1).strip().lower().rstrip('/')
    return None

def sync_files(source_file, target_files):
    if not os.path.exists(source_file):
        print(f"❌ 원본 파일({source_file})이 없습니다.")
        return

    # [기준] textURL.md에서 URL 목록 읽기
    with open(source_file, 'r', encoding='utf-8') as f:
        master_urls = [l.strip() for l in f if l.strip()]

    for target_path in target_files:
        if not os.path.exists(target_path):
            print(f"⏩ {target_path} 파일이 없어 건너뜁니다.")
            continue

        print(f"\n" + "="*50)
        print(f"🔍 대상 파일: {target_path}")
        
        # 대상 파일의 기존 내용 분석
        existing_lines = []
        existing_url_map = {} # {표준화URL: 원본줄}
        
        with open(target_path, 'r', encoding='utf-8') as f:
            for line in f:
                raw_line = line.strip()
                if not raw_line: continue
                
                pure = get_pure_url(raw_line)
                if pure:
                    # 파일 안에 이미 있는 URL이면 맵에 기록 (첫 발견된 형태 유지)
                    if pure not in existing_url_map:
                        existing_url_map[pure] = raw_line
        
        # 새로운 내용 구성 (기준 파일 순서대로)
        final_output = []
        added_count = 0
        
        for m_url in master_urls:
            m_pure = get_pure_url(m_url)
            
            if m_pure in existing_url_map:
                # [이미 있음] 주석이든 아니든 기존에 있던 형태 그대로 사용
                final_output.append(existing_url_map[m_pure])
                # 중복 방지를 위해 맵에서 제거 (나중에 중복 데이터가 뒤에 붙지 않게)
                del existing_url_map[m_pure]
            else:
                # [없음] 새로 추가
                final_output.append(m_url)
                print(f"  [+] 신규 추가: {m_url}")
                added_count += 1

        # 원본(master)에는 없지만 대상 파일에만 남아있던 나머지 줄들 추가
        for remaining_line in existing_url_map.values():
            final_output.append(remaining_line)

        # 파일 저장
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(final_output) + '\n')
        
        print(f"✅ 동기화 완료! (새로 추가된 URL: {added_count}개)")

# --- 설정부 ---
source = 'textURL.md'
targets = ['google.md', 'bing.md', 'naver.md']

if __name__ == "__main__":
    try:
        sync_files(source, targets)
        print("\n" + "★" * 25)
        print(" 모든 작업이 완료되었습니다.")
        print("★" * 25)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
    
    print("\n상세 로그를 확인하신 후 종료하려면 엔터를 누르세요.")
    input("Press Enter to exit...")