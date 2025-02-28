"""
Text Buffer Test Script
Version: 1.0
Timestamp: 2025-02-28 22:21 CET
"""
import sys
import time
from pathlib import Path
import unittest

# Add project directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.text import TextBuffer, TextSegment
import config

class TextBufferTest(unittest.TestCase):
    """Tests for the TextBuffer class"""
    
    def setUp(self):
        """Set up test environment"""
        # Use a smaller buffer size and age for testing
        self.buffer = TextBuffer(max_size=10, max_age=5.0)
    
    def test_add_segment(self):
        """Test adding segments to the buffer"""
        # Add a segment
        segment = self.buffer.add_segment("Test segment")
        
        # Verify segment properties
        self.assertEqual(segment.text, "Test segment")
        self.assertFalse(segment.processed)
        self.assertIsNone(segment.output)
        
        # Verify buffer state
        self.assertEqual(len(self.buffer.buffer), 1)
        self.assertEqual(len(self.buffer.text_lookup), 1)
        self.assertIn("test segment", self.buffer.text_lookup)
    
    def test_mark_processed(self):
        """Test marking segments as processed"""
        # Add a segment
        segment = self.buffer.add_segment("Test segment")
        
        # Mark as processed
        self.buffer.mark_processed(segment, "Processed output")
        
        # Verify segment state
        self.assertTrue(segment.processed)
        self.assertEqual(segment.output, "Processed output")
    
    def test_is_duplicate(self):
        """Test duplicate detection"""
        # Add a segment
        self.buffer.add_segment("This is a test segment")
        
        # Test exact match
        self.assertTrue(self.buffer.is_duplicate("This is a test segment"))
        
        # Test case insensitivity
        self.assertTrue(self.buffer.is_duplicate("THIS IS A TEST SEGMENT"))
        
        # Test whitespace normalization
        self.assertTrue(self.buffer.is_duplicate("  This   is  a  test  segment  "))
        
        # Test substring (existing text is substring of new text)
        self.assertTrue(self.buffer.is_duplicate("This is a test segment with more text"))
        
        # Test substring (new text is substring of existing text)
        self.assertTrue(self.buffer.is_duplicate("This is a test"))
        
        # Test non-duplicate
        self.assertFalse(self.buffer.is_duplicate("This is a different segment"))
    
    def test_get_recent_segments(self):
        """Test retrieving recent segments"""
        # Add multiple segments
        segment1 = self.buffer.add_segment("Segment 1")
        segment2 = self.buffer.add_segment("Segment 2")
        segment3 = self.buffer.add_segment("Segment 3")
        
        # Mark some as processed
        self.buffer.mark_processed(segment1, "Output 1")
        self.buffer.mark_processed(segment3, "Output 3")
        
        # Get all recent segments
        recent = self.buffer.get_recent_segments()
        self.assertEqual(len(recent), 3)
        
        # Get processed segments only
        processed = self.buffer.get_recent_segments(processed_only=True)
        self.assertEqual(len(processed), 2)
        self.assertEqual(processed[0].text, "Segment 1")
        self.assertEqual(processed[1].text, "Segment 3")
        
        # Get limited number of segments
        limited = self.buffer.get_recent_segments(count=2)
        self.assertEqual(len(limited), 2)
        self.assertEqual(limited[0].text, "Segment 1")
        self.assertEqual(limited[1].text, "Segment 2")
    
    def test_get_unprocessed_segments(self):
        """Test retrieving unprocessed segments"""
        # Add multiple segments
        segment1 = self.buffer.add_segment("Segment 1")
        segment2 = self.buffer.add_segment("Segment 2")
        segment3 = self.buffer.add_segment("Segment 3")
        
        # Mark some as processed
        self.buffer.mark_processed(segment1, "Output 1")
        
        # Get unprocessed segments
        unprocessed = self.buffer.get_unprocessed_segments()
        self.assertEqual(len(unprocessed), 2)
        self.assertEqual(unprocessed[0].text, "Segment 2")
        self.assertEqual(unprocessed[1].text, "Segment 3")
    
    def test_clear(self):
        """Test clearing the buffer"""
        # Add segments
        self.buffer.add_segment("Segment 1")
        self.buffer.add_segment("Segment 2")
        
        # Clear buffer
        self.buffer.clear()
        
        # Verify buffer state
        self.assertEqual(len(self.buffer.buffer), 0)
        self.assertEqual(len(self.buffer.text_lookup), 0)
    
    def test_cleanup_old_segments(self):
        """Test automatic cleanup of old segments"""
        # Add segments
        self.buffer.add_segment("Segment 1")
        self.buffer.add_segment("Segment 2")
        
        # Wait for segments to age
        time.sleep(6.0)  # Longer than max_age
        
        # Add a new segment to trigger cleanup
        self.buffer.add_segment("Segment 3")
        
        # Verify buffer state (old segments should be removed)
        self.assertEqual(len(self.buffer.buffer), 1)
        self.assertEqual(len(self.buffer.text_lookup), 1)
        self.assertIn("segment 3", self.buffer.text_lookup)
    
    def test_max_size_limit(self):
        """Test maximum size limit"""
        # Add more segments than max_size
        for i in range(15):  # max_size is 10
            self.buffer.add_segment(f"Segment {i}")
        
        # Verify buffer size
        self.assertEqual(len(self.buffer.buffer), 10)
        
        # Verify buffer contains only the most recent segments
        segments = [s.text for s in self.buffer.buffer]
        for i in range(5, 15):
            self.assertIn(f"Segment {i}", segments)

if __name__ == "__main__":
    unittest.main()
