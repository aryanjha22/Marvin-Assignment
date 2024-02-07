"""
Instructions for running test's:

    Install required packages if not already installed: pip install Flask wikipedia

    Run the test's using python3 test_assignment.py
"""

import unittest
from unittest.mock import patch
from flask import Flask
import wikipedia
from assignment import app

class WordFrequencyAppTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_word_frequency_analysis_success(self):
        # Test a successful request for word frequency analysis
        response = self.app.get('/word-frequency-analysis?topic=Newspaper&n=5')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Topic: Newspaper', response.data)
        self.assertIn(b'Top 5 Words:', response.data)

    def test_word_frequency_analysis_missing_topic(self):
        # Test a request with missing 'topic' parameter
        response = self.app.get('/word-frequency-analysis')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Error: Topic parameter is required', response.data)

    @patch('wikipedia.page')
    def test_word_frequency_analysis_disambiguation_error(self, mock_page):
        # Test handling DisambiguationError
        mock_page.side_effect = wikipedia.exceptions.DisambiguationError("Python", ["Python (programming)", "Python (snake)"])
        response = self.app.get('/word-frequency-analysis?topic=Python&n=5')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'DisambiguationError', response.data)
        self.assertIn(b'Python (programming)', response.data)
        self.assertIn(b'Python (snake)', response.data)

    @patch('wikipedia.page')
    def test_word_frequency_analysis_page_error(self, mock_page):
        # Test handling PageError
        mock_page.side_effect = wikipedia.exceptions.PageError("Page not found")
        response = self.app.get('/word-frequency-analysis?topic=aryan&n=5')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'PageError', response.data)
        self.assertIn(b'Page not found', response.data)

    def test_search_history_success(self):
        # Test a successful request for search history
        response = self.app.get('/search-history')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Search History:', response.data)

    def test_internal_server_error(self):
        # Test an internal server error
        with patch('wikipedia.page') as mock_page:
            mock_page.side_effect = Exception("Internal server error")
            response = self.app.get('/word-frequency-analysis?topic=Python&n=5')
            self.assertEqual(response.status_code, 500)
            self.assertIn(b'Internal Server Error', response.data)

if __name__ == '__main__':
    unittest.main()
