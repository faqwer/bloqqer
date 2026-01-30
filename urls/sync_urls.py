import os
import re

def get_pure_url(line):
    """
    URL에서 파라미터(?m=1 등)를 제외한 순수 경로만 추출하여 비교 데이터를 통일합니다.
    """
    clean = re.sub(r'', '', line).strip()
    match = re.search(r'(https?://[^\s<>"]+)', clean, re.IGNORECASE)
    if match:
        # 1. 소문자 변환 및 끝 슬래시 제거
        url = match.group(1).strip().lower().rstrip('/')
        # 2. 파라미터(? 이후 내용) 제거하여 순수 URL만 반환
        return url.split('?')[0]
    return None

def sync_files(source_file, target_files):
    if not os.path.exists(source_file):
        print(f"❌ 원본 파일({source_file})이 없습니다.")
        return

    # 기준 파일 읽기
    with open(source_file, 'r', encoding='utf-8') as f:
        master_lines = [l.strip() for l in f if l.strip()]

    for target_path in target_files:
        if not os.path.exists(target_path):
            print(f"⏩ {target_path} 파일이 없어 건너뜀.")
            continue

        is_google = os.path.basename(target_path).lower() == 'google.md'
        print(f"\n" + "="*50)
        print(f"🔍 대상 파일: {target_path} {' (Google 모드)' if is_google else ''}")
        
        existing_url_map = {} 
        
        # 대상 파일 분석
        with open(target_path, 'r', encoding='utf-8') as f:
            for line in f:
                raw_line = line.strip()
                if not raw_line: continue
                
                pure = get_pure_url(raw_line)
                # 여기서 pure는 ?m=1이 제거된 상태이므로, 
                # 이미 ?m=1이 붙어있던 줄도 동일한 Key로 저장됨
                if pure and pure not in existing_url_map:
                    existing_url_map[pure] = raw_line
        
        final_output = []
        added_count = 0
        
        # 기준 파일 순서대로 재구성
        for m_line in master_lines:
            m_pure = get_pure_url(m_line)
            
            if m_pure and m_pure in existing_url_map:
                # 이미 존재하면 기존 줄(이미 ?m=1이 붙어있을 수 있음) 사용
                target_line = existing_url_map[m_pure]
                del existing_url_map[m_pure]
            else:
                # 새로 추가
                target_line = m_line
                if m_pure: added_count += 1

            # Google 모드일 때만 파라미터 부착 (중복 부착 방지 포함)
            if is_google and m_pure and "?m=1" not in target_line:
                target_line = re.sub(r'(https?://[^\s<>"]+)', r'\1?m=1', target_line)
            
            final_output.append(target_line)

        # 나머지 데이터 처리 (Google 모드 적용)
        for remaining_line in existing_url_map.values():
            if is_google and get_pure_url(remaining_line) and "?m=1" not in remaining_line:
                remaining_line = re.sub(r'(https?://[^\s<>"]+)', r'\1?m=1', remaining_line)
            final_output.append(remaining_line)

        # 저장
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(final_output) + '\n')
        
        print(f"✅ 동기화 완료! (신규 추가: {added_count}개)")

if __name__ == "__main__":
    source = 'textURL.md'
    targets = ['google.md', 'bing.md', 'naver.md']
    try:
        sync_files(source, targets)
        print("\n모든 작업이 완료되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
    # input("\n종료하려면 엔터를 누르세요...")