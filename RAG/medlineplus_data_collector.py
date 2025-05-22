import requests
import re
import os
import xml.etree.ElementTree as ET
import time
from pathlib import Path
import html

# 출력 디렉토리 생성
OUTPUT_DIR = 'medlineplus_data'
Path(OUTPUT_DIR).mkdir(exist_ok=True)

def get_all_health_topics():
    """ MedlinePlus 건강 주제 목록 페이지에서 주제 추출
        출처 : https://medlineplus.gov/healthtopics_a.html    
    
        # 기본 대기 시간(1초)으로 실행
        python medlineplus_data_collector.py

        # 대기 시간을 3초로 설정하여 모든 주제 처리
        python medlineplus_data_collector.py --delay 3

        # 대기 시간을 0.5초로 설정하고 테스트 모드로 실행(5개 주제만)
        python medlineplus_data_collector.py --test --delay 0.5

        # 대기 시간을 2초로 설정하고 10개 주제만 처리
        python medlineplus_data_collector.py --topics 10 --delay 2
    """
    try:
        print("MedlinePlus 건강 주제 데이터 가져오는 중...")
        response = requests.get('https://medlineplus.gov/healthtopics_a.html')
        response.raise_for_status()  # 오류 발생 시 예외 발생
        html_content = response.text
        
        # 수정된 정규식 패턴으로 건강 주제 링크 추출
        # 1. 전체 URL 형식: <a href="https://medlineplus.gov/abdominalpain.html">Abdominal Pain</a>
        # 2. 상대 URL 형식: <a href="/abdominalpain.html">Abdominal Pain</a>
        topic_regex = r'<a href="(?:https://medlineplus\.gov/|/)([a-z0-9]+)\.html">(.*?)</a>'
        topics = []
        
        for match in re.finditer(topic_regex, html_content, re.IGNORECASE):
            topic_id = match.group(1)
            topic_name = match.group(2)
            topics.append({
                'id': topic_id,
                'name': topic_name
            })
        
        if topics:
            print(f"{len(topics)}개의 주제를 찾았습니다.")
        else:
            print("주제를 찾지 못했습니다. 디버깅 정보:")
            # 디버깅을 위해 페이지의 일부 내용 출력
            print(html_content[:500])
            print("...")
            print(html_content[-500:])
            
        return topics
    except Exception as e:
        print(f'건강 주제 목록을 가져오는 중 오류 발생: {e}')
        return []

def get_health_topic_details(topic_id, topic_name):
    """특정 건강 주제의 상세 정보 가져오기"""
    try:
        url = f'https://wsearch.nlm.nih.gov/ws/query?db=healthTopics&term=title:{topic_name}'
        response = requests.get(url)
        response.raise_for_status()
        xml_data = response.text
        
        # XML 데이터 파싱
        root = ET.fromstring(xml_data)
        
        # FullSummary 내용 추출
        full_summary = ''
        
        # XML 네임스페이스 처리
        namespaces = {'': root.tag.split('}')[0][1:] if '}' in root.tag else ''}
        
        # document 요소 찾기
        documents = root.findall('.//document', namespaces)
        
        for document in documents:
            contents = document.findall('.//content', namespaces)
            for content in contents:
                name = content.get('name')
                if name == 'FullSummary':
                    full_summary = content.text
                    break
            
            if full_summary:
                break
        
        # HTML 태그와 엔티티 제거 
        if full_summary:
            # HTML 태그 제거 (정규식 사용)
            full_summary = re.sub(r'<[^>]+>', '', full_summary)
            # HTML 엔티티 디코딩 (예: &amp; → &)
            full_summary = html.unescape(full_summary)
            
        return {
            'topic_name': topic_name,
            'full_summary': full_summary
        }
    except Exception as e:
        print(f"{topic_id} 주제의 상세 정보를 가져오는 중 오류 발생: {e}")
        return {
            'topic_name': topic_name,
            'full_summary': f'오류 발생: {e}'
        }

def save_all_health_topics(max_topics=None, is_test_mode=False):
    """모든 건강 주제에 대한 정보를 가져와 저장
    
    Args:
        max_topics (int, optional): 처리할 최대 주제 수. None이면 모든 주제 처리
        is_test_mode (bool, optional): 테스트 모드 여부. True이면 5개만 처리
    """
    print('MedlinePlus 건강 주제 정보 추출 시작...')
    
    # 모든 건강 주제 가져오기
    topics = get_all_health_topics()
    total_topics = len(topics)
    print(f'총 {total_topics}개의 건강 주제를 찾았습니다.')
    
    # 테스트 모드이면 5개만 처리
    if is_test_mode:
        process_topics = 5
        print(f'테스트 모드: 처음 {process_topics}개 주제만 처리합니다.')
    elif max_topics is not None:
        process_topics = min(max_topics, total_topics)
        print(f'지정된 {max_topics}개 중 {process_topics}개 주제를 처리합니다.')
    else:
        process_topics = total_topics
        print(f'모든 {total_topics}개 주제를 처리합니다.')
    
    # 각 주제별로 상세 정보 가져오기
    for i, topic in enumerate(topics[:process_topics]):
        print(f'({i+1}/{process_topics}) {topic["name"]} 주제 처리 중...')
        
        details = get_health_topic_details(topic['id'], topic['name'])
        
        # 텍스트 파일로 저장
        filename = os.path.join(OUTPUT_DIR, f"{topic['id']}.txt")
        content = f"주제: {topic['name']}\n\n{details['full_summary']}"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'  - {filename} 파일에 저장 완료')
        
        # API 서버 부하를 줄이기 위한 지연
        time.sleep(1)
    
    print('모든 처리가 완료되었습니다.')

def save_specific_topic(topic_id, topic_name):
    """특정 주제만 가져오기"""
    print(f'{topic_name} 주제 정보 추출 시작...')
    
    details = get_health_topic_details(topic_id, topic_name)
    
    # 텍스트 파일로 저장
    filename = os.path.join(OUTPUT_DIR, f"{topic_id.lower().replace(' ', '_')}.txt")
    content = f"주제: {topic_name}\n\n{details['full_summary']}"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'{filename} 파일에 저장 완료')

if __name__ == "__main__":
    import argparse
    
    # 명령줄 인자 파서 설정
    parser = argparse.ArgumentParser(description='MedlinePlus 건강 주제 정보 추출 도구')
    parser.add_argument('--test', action='store_true', help='테스트 모드: 5개 주제만 처리')
    parser.add_argument('--topics', type=int, help='처리할 주제 개수 (기본값: 모두)')
    parser.add_argument('--specific', type=str, help='특정 주제 ID를 처리 (예: asthma)')
    args = parser.parse_args()
    
    if args.specific:
        # 특정 주제만 처리
        print(f"특정 주제 '{args.specific}' 처리 모드")
        save_specific_topic(args.specific, args.specific.capitalize())
    else:
        # 모든 주제 처리 (또는 지정된 개수만큼)
        topics = get_all_health_topics()
        
        if topics:
            print("주제 목록 (처음 5개 예시):")
            for i, topic in enumerate(topics[:5]):
                print(f"{i+1}. {topic['name']} (ID: {topic['id']})")
            
            # 주제 처리
            if args.test:
                # 테스트 모드: 5개만 처리
                save_all_health_topics(is_test_mode=True)
            elif args.topics:
                # 지정된 개수만큼 처리
                save_all_health_topics(max_topics=args.topics)
            else:
                # 모든 주제 처리
                save_all_health_topics()
        else:
            print("주제를 가져오지 못했습니다. 직접 주제 ID를 지정하여 처리합니다.")
            # 기본 주제 ID 직접 지정
            save_specific_topic('asthma', 'Asthma')