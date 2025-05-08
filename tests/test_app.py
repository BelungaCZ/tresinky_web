import unittest
import os
import tempfile
from werkzeug.datastructures import FileStorage

def test_home_page(client):
    """Test if home page loads successfully"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'T\xc5\x99e\xc5\xa1inky Cetechovice' in response.data

def test_about_page(client):
    """Test if about page loads successfully"""
    response = client.get('/o-nas')
    assert response.status_code == 200
    assert b'O n\xc3\xa1s' in response.data

def test_garden_page(client):
    """Test if garden page loads successfully"""
    response = client.get('/sad')
    assert response.status_code == 200
    assert b'Sad' in response.data

def test_support_page(client):
    """Test if support page loads successfully"""
    response = client.get('/podpora')
    assert response.status_code == 200
    assert b'Podpora' in response.data

def test_contact_page(client):
    """Test if contact page loads successfully"""
    response = client.get('/kontakt')
    assert response.status_code == 200
    assert b'Kontakt' in response.data 