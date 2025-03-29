# CodeBug Analyzer

CodeBug Analyzer is a comprehensive code analysis tool that scans repositories for bugs and generates detailed reports. It helps developers identify potential bugs and issues in their code, focusing on best practices and common programming mistakes.

![CodeBug Analyzer](generated-icon.png)

## Features

- **Repository Analysis**: Scan GitHub repositories for potential bugs and code issues
- **Multi-Language Support**: Analyze Python, JavaScript, and Go codebases
- **Comprehensive Reports**: Generate visual and detailed reports of all identified issues
- **Individual Bug Reports**: Export detailed bug reports for each identified issue
- **Severity Categorization**: Issues are categorized by severity (critical, high, medium, low, info)
- **Language Statistics**: View statistics about language usage and bug density
- **Code Snippets**: View problematic code with context to help understand the issues

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- PostgreSQL (optional, SQLite is used by default)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/codebug-analyzer.git
   cd codebug-analyzer
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python main.py
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

### Using Docker (Alternative)

```bash
docker build -t codebug-analyzer .
docker run -p 5000:5000 codebug-analyzer
```

## Usage

1. **Enter a GitHub Repository URL**
   - Go to the home page and enter a GitHub repository URL in the form
   - Click "Analyze Repository" to start the analysis

2. **View Analysis Results**
   - The application will display a comprehensive report of all bugs found
   - View statistics about bug severity, affected files, and language distribution
   - Browse the list of individual bugs with details

3. **Generate Individual Bug Reports**
   - Click "Generate Individual Reports" to create detailed reports for each bug
   - Reports are saved in the `results/<repository-name>` directory
   - Click "View Individual Reports" to access and download the reports

## Configuration

The application can be configured using environment variables:

- `DATABASE_URL`: Database connection string (default: SQLite)
- `SESSION_SECRET`: Secret key for session management
- `DEBUG`: Enable debug mode (set to True/False)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Flask, SQLAlchemy, and Bootstrap
- Uses GitPython for repository handling
- Chart visualizations powered by Chart.js