# StackScout Job Recommendations System

## Overview

This document provides comprehensive documentation for the Job Recommendations Engine (Phase 2) implementation in StackScout.

## Features Implemented

### ✅ Core Recommendation Engine

- **Personalized Job Matching**: AI-powered job recommendations based on user profile and behavior
- **Skill-Based Matching**: TF-IDF and cosine similarity for skill matching
- **User Behavior Analysis**: Tracks views, saves, applications, and ignores
- **Real-time Scoring**: Dynamic match scoring with configurable weights

### ✅ Database Schema

- **User Job Interactions**: Tracks all user interactions with jobs
- **Search History**: Stores user search queries for personalization
- **Recommendation Cache**: Pre-computed recommendations for performance
- **User Preferences**: Advanced recommendation preferences system

### ✅ API Endpoints

- `POST /recommendations/jobs` - Get personalized job recommendations
- `POST /recommendations/interaction` - Record user interactions
- `GET /recommendations/stats` - Get recommendation statistics
- `GET /recommendations/config` - Get algorithm configuration
- `PUT /recommendations/config` - Update algorithm configuration
- `GET /recommendations/health` - Health check endpoint

### ✅ Security & Integration

- JWT authentication integration
- User-specific recommendation isolation
- Protected endpoints with proper authorization
- Integration with existing authentication system

## Quick Start

### 1. Install Dependencies

```bash
python setup_recommendations.py
```

### 2. Manual Setup (Alternative)

```bash
# Install machine learning dependencies
pip install scikit-learn numpy scipy

# Set up database schema
psql -d job_scraper_db -f create_recommendations_schema.sql
```

### 3. Start the Server

```bash
python stackscout_web.py
```

## API Usage Examples

### Get Job Recommendations

```bash
curl -X POST http://localhost:8000/recommendations/jobs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "user_id": 1,
    "limit": 10,
    "include_saved": false
  }'
```

### Record Job Interaction

```bash
curl -X POST "http://localhost:8000/recommendations/interaction?job_id=123&interaction_type=view&duration=30" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get Recommendation Statistics

```bash
curl -X GET http://localhost:8000/recommendations/stats \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Algorithm Configuration

The recommendation algorithm uses weighted scoring with the following default weights:

- **Skill Matching**: 40% (TF-IDF cosine similarity)
- **Experience Level**: 30%
- **Location Preference**: 10%
- **Salary Range**: 10%
- **Company Preference**: 10%

### Customizing Weights

```bash
curl -X PUT http://localhost:8000/recommendations/config \
  -H "Content-Type: application/json" \
  -d '{
    "skill_weight": 0.5,
    "experience_weight": 0.2,
    "location_weight": 0.1,
    "salary_weight": 0.1,
    "company_weight": 0.1,
    "min_match_score": 0.3,
    "max_recommendations": 50
  }'
```

## Database Schema Details

### User Job Interactions Table

Tracks all user interactions with jobs for recommendation personalization:

- `user_id`: Reference to users table
- `job_id`: Reference to jobs table  
- `interaction_type`: 'view', 'save', 'apply', or 'ignore'
- `duration`: Time spent viewing (seconds)
- `interaction_date`: Timestamp of interaction

### Search History Table

Stores user search queries for understanding preferences:

- `search_query`: JSON object with search parameters
- `result_count`: Number of jobs returned
- `search_date`: Timestamp of search

### Recommendation Cache Table

Pre-computed recommendations for performance:

- `match_score`: Similarity score (0-1)
- `match_reasons`: JSON array of match reasons
- `expires_at`: Cache expiration timestamp

## Machine Learning Features

### Skill Extraction

- Uses TF-IDF vectorization with n-grams (1-2)
- 1000+ technical skill keywords predefined
- Customizable skill dictionary

### Similarity Scoring

- Cosine similarity between job descriptions and user skills
- Dynamic weighting based on user behavior
- Configurable minimum match threshold

### Personalization

- Learns from user interactions (views, saves, applications)
- Adapts to search history and preferences
- Improves over time with more data

## Testing

Run the comprehensive test suite:

```bash
python test_recommendations.py
```

## Integration Points

### With Authentication System

- Uses JWT tokens for user identification
- Integrates with user preferences from auth system
- Respects user privacy and data isolation

### With Job Storage

- Reads from existing jobs table
- Supports all job platforms (LinkedIn, Indeed, etc.)
- Handles job metadata and descriptions

### With AI Generators

- Potential future integration with resume/CV analysis
- Could use AI-generated profiles for better matching
- Complementary to existing AI features

## Performance Considerations

- **Caching**: Pre-computed recommendations with expiration
- **Indexing**: Comprehensive database indexes for fast queries
- **Batch Processing**: Efficient bulk operations
- **Memory Management**: Streaming data processing where possible

## Monitoring & Analytics

- Health check endpoint for system monitoring
- Detailed interaction statistics
- Performance metrics tracking
- Error logging and alerting

## Future Enhancements

1. **Advanced ML Models**: Neural networks for better matching
2. **Real-time Learning**: Online learning from interactions
3. **Multi-modal Matching**: Combine skills, culture, values
4. **A/B Testing**: Experiment with different algorithms
5. **Notification System**: Push recommendations via email/notifications
6. **Collaborative Filtering**: User-user similarity recommendations

## Troubleshooting

### Common Issues

1. **No Recommendations**: Check if jobs exist in database
2. **Low Match Scores**: Adjust algorithm weights or add more user data
3. **Database Errors**: Verify database connection and schema
4. **Authentication Issues**: Check JWT token validity

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Support

For issues with the recommendation system:

1. Check the health endpoint: `/recommendations/health`
2. Review application logs
3. Verify database connectivity
4. Test with the provided test script

---
**Phase 2 Complete**: Job Recommendations Engine successfully implemented and integrated! 🎉
