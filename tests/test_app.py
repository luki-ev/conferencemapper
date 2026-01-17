import pytest
import hashlib
import urllib.parse
from unittest.mock import patch
import fakeredis
from conferencemapper.app import app, digits


def encode_conference_name(name):
    """Helper function to encode conference names using the same logic as the app."""
    return urllib.parse.quote(name.lower(), safe='/@')


@pytest.fixture
def redis_mock():
    """Create a fake Redis client for testing."""
    return fakeredis.FakeRedis()


@pytest.fixture
def client(redis_mock):
    """Create a test client for the Flask app with mocked Redis."""
    app.config['TESTING'] = True
    
    # Patch the Redis instance in the app module
    with patch('conferencemapper.app.r', redis_mock):
        with app.test_client() as client:
            yield client


class TestConferenceMapper:
    """Tests for the conference mapper endpoint."""

    def test_mapper_with_conference_parameter(self, client):
        """Test creating a conference mapping with conference parameter."""
        conference_name = "testroom"
        response = client.get(f'/conferenceMapper?conference={conference_name}')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['message'] == "Successfully retrieved conference mapping"
        assert 'id' in data
        assert data['conference'] == conference_name
        
        # Verify the ID is correctly calculated
        expected_id = int(hashlib.sha1(conference_name.encode("utf-8")).hexdigest(), 16) % 10**digits
        assert data['id'] == expected_id

    def test_mapper_with_uppercase_conference(self, client):
        """Test that conference names are lowercased before ID generation."""
        conference_upper = "TestRoom"
        conference_lower = "testroom"
        
        response_upper = client.get(f'/conferenceMapper?conference={conference_upper}')
        response_lower = client.get(f'/conferenceMapper?conference={conference_lower}')
        
        assert response_upper.status_code == 200
        assert response_lower.status_code == 200
        
        data_upper = response_upper.get_json()
        data_lower = response_lower.get_json()
        
        # Both should generate the same ID
        assert data_upper['id'] == data_lower['id']
        # Conference should be lowercased
        assert data_upper['conference'] == conference_lower

    def test_mapper_with_special_characters(self, client, redis_mock):
        """Test URL encoding with special characters in conference name."""
        conference_name = "test room@conference"
        response = client.get(f'/conferenceMapper?conference={urllib.parse.quote(conference_name)}')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['message'] == "Successfully retrieved conference mapping"
        assert 'id' in data
        # Conference name should be lowercased
        assert data['conference'] == conference_name.lower()
        
        # Verify the stored value in Redis is URL-encoded
        conf_id = data['id']
        stored_value = redis_mock.get(conf_id)
        expected_encoded = encode_conference_name(conference_name)
        assert stored_value.decode('utf-8') == expected_encoded

    def test_mapper_retrieve_with_id(self, client):
        """Test retrieving a conference by ID."""
        conference_name = "myroom"
        
        # First, create a mapping
        response_create = client.get(f'/conferenceMapper?conference={conference_name}')
        assert response_create.status_code == 200
        conf_id = response_create.get_json()['id']
        
        # Now retrieve by ID
        response_retrieve = client.get(f'/conferenceMapper?id={conf_id}')
        assert response_retrieve.status_code == 200
        data = response_retrieve.get_json()
        
        assert data['message'] == "Successfully retrieved conference mapping"
        assert data['id'] == conf_id
        assert data['conference'] == conference_name

    def test_mapper_retrieve_nonexistent_id(self, client):
        """Test retrieving a non-existent conference ID."""
        non_existent_id = 999999
        response = client.get(f'/conferenceMapper?id={non_existent_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['message'] == "No conference mapping was found"
        assert data['id'] == non_existent_id
        assert data['conference'] is False

    def test_mapper_with_invalid_id(self, client):
        """Test with invalid (non-numeric) ID parameter."""
        response = client.get('/conferenceMapper?id=invalid')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['message'] == "No conference or id provided"
        assert data['conference'] is False
        assert data['id'] is False

    def test_mapper_no_parameters(self, client):
        """Test mapper endpoint with no parameters."""
        response = client.get('/conferenceMapper')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['message'] == "No conference or id provided"
        assert data['conference'] is False
        assert data['id'] is False

    def test_mapper_id_consistency(self, client):
        """Test that the same conference name always generates the same ID."""
        conference_name = "consistencytest"
        
        response1 = client.get(f'/conferenceMapper?conference={conference_name}')
        response2 = client.get(f'/conferenceMapper?conference={conference_name}')
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.get_json()
        data2 = response2.get_json()
        
        assert data1['id'] == data2['id']

    def test_mapper_url_safe_characters(self, client, redis_mock):
        """Test that @ and / are treated as safe characters in URL encoding."""
        conference_name = "room@conference/test"
        response = client.get(f'/conferenceMapper?conference={urllib.parse.quote(conference_name)}')
        
        assert response.status_code == 200
        data = response.get_json()
        conf_id = data['id']
        
        # Check the stored value in Redis
        stored_value = redis_mock.get(conf_id)
        expected_encoded = encode_conference_name(conference_name)
        assert stored_value.decode('utf-8') == expected_encoded
        # Verify @ and / are not encoded
        assert '@' in stored_value.decode('utf-8')
        assert '/' in stored_value.decode('utf-8')

    def test_mapper_empty_conference_name(self, client):
        """Test with empty conference name parameter."""
        response = client.get('/conferenceMapper?conference=')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Empty string is falsy, so should return no conference/id provided
        assert data['message'] == "No conference or id provided"
        assert data['conference'] is False
        assert data['id'] is False
