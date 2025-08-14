# GENESIS API Testing with Bruno

This directory contains comprehensive API test collections using Bruno - a Git-friendly alternative to Postman for API testing.

## Setup

### Install Bruno

```bash
# macOS
brew install bruno

# Linux/Windows
# Download from: https://www.usebruno.com/downloads
```

### Environment Configuration

1. **Local Development**
   - Use `local.bru` environment
   - Ensure backend is running on `localhost:8000`
   - Update secret variables in Bruno app

2. **Staging Environment**
   - Use `staging.bru` environment
   - Configure staging API URL and credentials

3. **Production Environment**
   - Use `production.bru` environment
   - Configure production API URL and credentials

## Test Collections

### 1. Health Check

- **Health Status**: Basic health endpoint validation
- **Metrics Endpoint**: Prometheus metrics accessibility

### 2. Authentication

- **Sign Up**: User registration flow
- **Sign In**: User authentication with JWT tokens
- **Token Refresh**: JWT token renewal

### 3. Agents

- **List Agents**: Retrieve available AI agents
- **Chat with BLAZE**: Training-focused agent interaction
- **Chat with SAGE**: Nutrition-focused agent interaction

### 4. Voice

- **Synthesize Speech**: ElevenLabs voice synthesis
- **List Voices**: Available voice options

### 5. Chat

- **Send Message**: Direct chat messaging
- **Get Conversations**: Conversation history

### 6. Feature Flags

- **Get Feature Flags**: Runtime feature toggles

## Running Tests

### Individual Tests

1. Open Bruno application
2. Import this collection
3. Select appropriate environment
4. Run individual requests

### Collection Runner

1. Select collection in Bruno
2. Choose environment
3. Use "Run Collection" feature
4. Review results and export reports

### Command Line (Bruno CLI)

```bash
# Install Bruno CLI
npm install -g @usebruno/cli

# Run entire collection
bru run --env local

# Run specific folder
bru run --env local --folder "Authentication"

# Export results
bru run --env local --output results.json
```

## Test Flow

### Recommended Test Sequence

1. **Health Check** - Verify API availability
2. **Authentication** - Get authentication token
3. **Agents** - Test agent interactions
4. **Chat** - Test conversation flows
5. **Voice** - Test voice synthesis
6. **Feature Flags** - Verify feature availability

### Authentication Flow

Tests are designed to run in sequence:

1. Sign Up creates test user (if needed)
2. Sign In provides authentication token
3. Token is automatically stored for subsequent requests
4. Token Refresh updates expired tokens

## Environment Variables

### Automatic Variables

- `auth_token` - JWT token from successful login
- `refresh_token` - Refresh token for token renewal
- `user_id` - User ID extracted from JWT
- `conversation_id` - Active conversation ID

### Secret Variables (Configure in Bruno)

- `test_user_email` - Test user email address
- `test_user_password` - Test user password
- `elevenlabs_api_key` - ElevenLabs API key for voice

## Test Validation

### Response Validation

Each test includes comprehensive validation:

- HTTP status codes
- Response structure validation
- Required field presence
- Data type verification
- Business logic validation

### Performance Testing

- Response time thresholds
- Reasonable timeouts for AI operations
- Health check performance requirements

### Error Handling

- Authentication error scenarios
- Invalid request validation
- Service unavailability handling

## Continuous Integration

### GitHub Actions Integration

```yaml
name: API Tests
on: [push, pull_request]
jobs:
  api-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: npm install -g @usebruno/cli
      - run: bru run --env local --output api-test-results.json
      - uses: actions/upload-artifact@v4
        with:
          name: api-test-results
          path: api-test-results.json
```

### Test Reporting

- JSON output for automated processing
- HTML reports for manual review
- Performance metrics tracking
- Error rate monitoring

## Best Practices

### Request Organization

- Logical grouping by functionality
- Sequential numbering for execution order
- Descriptive naming conventions

### Test Data Management

- Environment-specific test data
- Dynamic data generation using `{{$timestamp}}`
- Cleanup procedures for test data

### Error Handling

- Graceful handling of authentication failures
- Retry logic for transient failures
- Detailed error reporting

### Security

- Secure storage of API keys and passwords
- Token rotation and refresh
- Environment separation

## Troubleshooting

### Common Issues

#### Authentication Failures

1. Verify credentials in environment secrets
2. Check token expiration and refresh
3. Validate API endpoint availability

#### Agent Response Issues

1. Check agent availability in `/agents` endpoint
2. Verify message format and structure
3. Monitor response times for AI operations

#### Voice Synthesis Problems

1. Validate ElevenLabs API key
2. Check voice ID availability
3. Verify text input format

### Debug Mode

Enable detailed logging in Bruno:

1. Open Bruno settings
2. Enable "Show Request/Response Details"
3. Check network tab for detailed information

## Contributing

### Adding New Tests

1. Create test in appropriate folder
2. Follow naming convention
3. Include comprehensive validation
4. Update documentation

### Test Data Updates

1. Update environment files
2. Modify sample payloads as needed
3. Ensure backward compatibility

### Performance Benchmarks

1. Set reasonable timeout thresholds
2. Monitor and update performance expectations
3. Document performance requirements
