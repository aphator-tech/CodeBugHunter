# CodeBug Analyzer - Technical Documentation

## Architecture Overview

CodeBug Analyzer is built with a modular architecture that separates concerns and allows for extensibility. The application follows the MVC (Model-View-Controller) pattern with Flask as the web framework.

### High-Level Components

```
┌─────────────────┐         ┌───────────────┐         ┌─────────────────┐
│                 │         │               │         │                 │
│  Web Interface  ├────────►│  Controllers  ├────────►│     Models      │
│                 │         │               │         │                 │
└────────┬────────┘         └───────┬───────┘         └────────┬────────┘
         │                          │                          │
         │                          ▼                          │
         │                  ┌───────────────┐                  │
         │                  │               │                  │
         └─────────────────►│   Services    │◄─────────────────┘
                            │               │
                            └───────┬───────┘
                                    │
                                    ▼
                             ┌──────────────┐
                             │              │
                             │  Analyzers   │
                             │              │
                             └──────────────┘
```

## Core Components

### 1. Models

The database structure is defined using SQLAlchemy models:

- **Repository**: Stores information about analyzed repositories
  - Fields: id, url, name, last_analyzed, status
  - Relationships: scans (one-to-many)

- **Scan**: Represents an analysis session of a repository
  - Fields: id, repository_id, timestamp, total_files, analyzed_files, total_bugs
  - Relationships: bugs (one-to-many), language_stats (one-to-many)

- **Bug**: Stores details about identified bugs
  - Fields: id, scan_id, file_path, line_number, bug_type, severity, description, code_snippet, recommendation, language

- **LanguageStats**: Tracks statistics about language usage
  - Fields: id, scan_id, language, file_count, line_count, bug_count

### 2. Services

Services handle the business logic of the application:

- **repository.py**: Manages repository operations (cloning, cleaning up)
  - Functions: clone_repository, cleanup_repository, get_repository_name, list_files

- **analyzer.py**: Coordinates the analysis process
  - Functions: analyze_repository

- **language_detector.py**: Identifies programming languages
  - Functions: detect_language, count_lines, analyze_language_stats

- **report_generator.py**: Creates summary reports
  - Functions: generate_report

- **individual_report_generator.py**: Generates detailed reports for individual bugs
  - Functions: generate_individual_bug_reports, generate_bug_report, ensure_repo_directory

### 3. Analyzers

Language-specific analyzers implement bug detection logic:

- **common_analyzer.py**: Checks common issues across all languages
  - Functions: analyze_common_issues, check_file_size, get_code_snippet

- **python_analyzer.py**: Python-specific bug detection
  - Classes: PythonAstVisitor (extends ast.NodeVisitor)
  - Functions: analyze_python_file

- **javascript_analyzer.py**: JavaScript/TypeScript bugs detection
  - Functions: analyze_javascript_file, check_for_strict_equality

- **go_analyzer.py**: Go language bug detection
  - Functions: analyze_go_file

## Database Schema

```
┌────────────────┐       ┌────────────────┐       ┌────────────────┐
│  Repository    │       │     Scan       │       │      Bug       │
├────────────────┤       ├────────────────┤       ├────────────────┤
│ id             │       │ id             │       │ id             │
│ url            │       │ repository_id  ├───┐   │ scan_id        ├───┐
│ name           │       │ timestamp      │   │   │ file_path      │   │
│ last_analyzed  │◄──────┤ total_files    │   │   │ line_number    │   │
│ status         │       │ analyzed_files │   │   │ bug_type       │   │
└────────────────┘       │ total_bugs     │   │   │ severity       │   │
                         └────────────────┘   │   │ description    │   │
                                              │   │ code_snippet   │   │
                                              │   │ recommendation │   │
                                              │   │ language       │   │
                                              │   └────────────────┘   │
                                              │                        │
                                              │   ┌────────────────┐   │
                                              │   │  LanguageStats │   │
                                              │   ├────────────────┤   │
                                              │   │ id             │   │
                                              └───┤ scan_id        │   │
                                                  │ language       │   │
                                                  │ file_count     │   │
                                                  │ line_count     │   │
                                                  │ bug_count      │◄──┘
                                                  └────────────────┘
```

## Flow of Operation

1. **User Submits Repository URL**
   - Form submission handled by routes.py (analyze function)
   - URL validation and repository creation in database

2. **Repository Cloning**
   - services/repository.py clones the GitHub repository
   - Clone is saved to a temporary directory

3. **Code Analysis**
   - services/analyzer.py coordinates the analysis process
   - Language detection for each file 
   - Language-specific analyzers process files
   - Bugs are identified and stored in the database

4. **Report Generation**
   - Summary report is generated with statistics
   - Charts and visualizations are created for the web interface
   - Individual bug reports can be generated on demand

5. **Results Display**
   - Web interface shows comprehensive report
   - Users can browse bugs, filter by severity
   - Report includes charts for visualization

## Individual Bug Reports

The application generates detailed reports for each identified bug in JSON format. These reports include:

```json
{
  "general_info": {
    "vulnerability_title": "Bug type in filename",
    "description": "Detailed description of the bug",
    "target": {
      "repository": "Repository name",
      "repository_url": "GitHub URL",
      "file_path": "Path to affected file",
      "line_number": 42,
      "language": "Programming language"
    },
    "vulnerability_category": "Bug type",
    "timestamp": "ISO timestamp"
  },
  "severity": {
    "level": "critical|high|medium|low|info",
    "score": "CVSS-like score range",
    "vector": "CVSS vector string"
  },
  "details": {
    "description": "Detailed explanation",
    "code_snippet": "Problematic code",
    "recommendation": "How to fix the issue"
  },
  "validation": {
    "steps": [
      "Step 1: Navigate to file",
      "Step 2: Go to line number",
      "Step 3: Observe the problem"
    ]
  }
}
```

## Routes

The application defines the following routes:

- **/** (index): Home page with repository submission form
- **/analyze** (POST): Handles repository analysis request
- **/results/<scan_id>**: Displays analysis results
- **/scan/<scan_id>/generate-reports**: Generates individual bug reports
- **/scan/<scan_id>/reports**: Displays the list of generated reports
- **/results/<path>**: Serves individual report files
- **/api/scans**: JSON API for scan listing
- **/api/scan/<scan_id>/bugs**: JSON API for bugs in a scan

## Security Considerations

- Repository URLs are validated before cloning
- Only GitHub repositories are supported to prevent potential security issues
- Temporary files are cleaned up after analysis
- User sessions are secured with a secret key
- Database connections use connection pooling and reconnection

## Performance Optimization

- Large repositories are analyzed file by file to manage memory usage
- Database queries use pagination for bug listing
- Report generation is done on-demand for individual bug reports
- Images and assets are cached by the browser

## Deployment

The application can be deployed using various methods:

### Option 1: Traditional Deployment

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables
4. Run with gunicorn: `gunicorn --bind 0.0.0.0:5000 main:app`

### Option 2: Docker Deployment

1. Build the Docker image: `docker build -t codebug-analyzer .`
2. Run the container: `docker run -p 5000:5000 -e DATABASE_URL=<your-db-url> codebug-analyzer`

### Option 3: Platform as a Service (PaaS)

The application is compatible with platforms like Heroku:

```
# Procfile
web: gunicorn main:app
```

## Extending the Application

### Adding Support for New Languages

1. Create a new analyzer in the `analyzers` directory (e.g., `rust_analyzer.py`)
2. Implement the language-specific bug detection logic
3. Update `services/language_detector.py` to recognize the new language
4. Integrate the new analyzer in `services/analyzer.py`

### Adding New Bug Detection Rules

1. Identify the appropriate analyzer for the language
2. Add new detection logic as functions in the analyzer
3. Update the analyzer's main function to call the new detection logic
4. Add test cases to validate the new detection rules

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | Database connection URL | sqlite:///code_analyzer.db |
| SESSION_SECRET | Secret key for Flask sessions | Random value |
| DEBUG | Enable/disable debug mode | True |
| REPO_TEMP_DIR | Directory for temporary repository clones | temp_repos/ |

## Requirements

- Python 3.11+
- Flask
- Flask-SQLAlchemy
- GitPython
- gunicorn (for production)
- psycopg2-binary (for PostgreSQL support)

## Troubleshooting

### Common Issues

1. **Repository cloning fails**
   - Ensure the GitHub repository is public
   - Check internet connectivity
   - Verify Git is installed and in the PATH

2. **Analysis takes too long**
   - Large repositories may require more time
   - Consider limiting analysis to specific directories
   - Ensure sufficient system resources

3. **Database errors**
   - Check DATABASE_URL environment variable
   - Ensure database server is running
   - Verify database user has proper permissions