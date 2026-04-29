import pytest

from routes import app

"""
Test for verifying Flask routes and API endpoints.
"""

# pytest framework: fixtures
@pytest.fixture

def client():
    # 테스트해보기 위해, Flask client 설정
    # 서버를 실제로 실행하지 않고도, 가상으로 요청을 보내고 응답 확인 가능 
    with app.test_client() as client:
        yield client

def test_index_route(client):
    # Main Dashboard page(GET /)가 잘 뜨는지 확인
    response = client.get('/')
    # 응답코드 200(성공)인지 확인 
    assert response.status_code == 200

def test_observation_list_api(client):
    # 전체 날씨 기록을 조회하는 API(GET /observations)
    # 결과가 JSON 리스트 형식으로 잘 들어오는지 확인
    response = client.get('/observations')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_ingest_missing_parameters(client):
    # 데이터 입력 시 필수파라미터(도시, 국가)가 빠진 경우 
    # 400 에러 + 에러 메시지를 모두 잘 보내는지 확인 
    
    # 파라미터 없이 요청 보냄 
    response = client.post('/ingest') 
    
    assert response.status_code == 400
    assert b"error" in response.data

def test_get_invalid_observation_id(client):
    # DB에 없는 ID를 조회하려고 할 때 에러 처리  
    # --> 정상적으로 404 Not Found 응답이 오는지 확인 
    
    # 존재하지 않는 ID (e.g. 123456)
    response = client.get('/observations/123456')
    assert response.status_code == 404
    assert b"error" in response.data

def test_delete_non_existent_id(client):
    # 없는 데이터를 삭제하려고 할 때 시스템이 에러를 내보내는지 확인 
    response = client.delete('/observations/123456')
    assert response.status_code == 404